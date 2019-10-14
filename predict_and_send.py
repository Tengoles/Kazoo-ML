import sys
from flaskr import model_settings
from datetime import datetime, timedelta
import os
import traceback
import zlib
import urllib.request
import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import json
import time
import math
#from sklearn import model_selection
#from sklearn.metrics import classification_report
#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
#from sklearn.model_selection import StratifiedKFold
#from sklearn.model_selection import StratifiedShuffleSplit
import pickle
from xgboost import XGBClassifier

ENDPOINT_URL = 'https://api.qa.kazooanalytics.com/api/v2/hub/logs'

def append_entries_json(dirPATH):
	files = os.listdir(dirPATH)
	files.sort()
	data_cruda = []
	for f in files:
		print(f)
		if ".json" in f:
			with open(dirPATH + f) as json_file:
				data_cruda.extend(json.loads(json_file.read()))
	DF = pd.DataFrame(data_cruda)
	DF['fechahora'] = pd.to_datetime(DF['fechahora'], format="%Y-%m-%d %H:%M:%S.%f")
	return DF

# esta funcion agarra el dataset, le modifica el formato de la
# informacion y lo envia como la informacion de varios falsos HUB
def process_and_send(dataset):
	for zona in list(dataset.Zona.unique()):
		if zona == "Afuera":
			continue
		print("Procesando " + zona)
		reduced_file_data = []
		data_zona = dataset[dataset['Zona'] == zona]
		for row in data_zona.itertuples():
			for column in row:
				if math.isnan(column):
					pass
				else:
					RSSI = column
					break
			entry = {'datetime': str(row.fechahora),
					 'mac_phone': row.MAC,
					 'rssi': str(RSSI)}
			reduced_file_data.append(entry)

		data_to_send = {
			'hub_identificator': zona,
			'data': reduced_file_data
		}
		print("Enviando " + zona)
		data_to_send = json.dumps(data_to_send)
		print("Comprimiendo")
		compressed_data_to_send = zlib.compress(data_to_send.encode('utf-8'))
		print('>>> ' + str(sys.getsizeof(data_to_send)))
		print('>>> ' + str(sys.getsizeof(compressed_data_to_send)))
		req = urllib.request.Request(ENDPOINT_URL, compressed_data_to_send)
		req.add_header('Content-Length', '%d' % len(compressed_data_to_send))
		req.add_header('Content-Encoding', 'application/octet-stream')
		response = urllib.request.urlopen(req)
		content = response.read()
		with open(model_settings.LOG_FILE, "a") as logFile:
			logFile.write("Enviado %s a Kazoo, respuesta: %s\n " % (zona, str(response.getcode())))
		print("Enviado %s a Kazoo, respuesta: %s\n " % (zona, str(response.getcode())))
		print("Contenido: %s\n" % content)

class TransitionError(Exception):
	def __init__(self, message):
		self.message = message


if __name__ == "__main__":
	try:
		hubs = model_settings.HUBS
		#invierto los elementos de la lista de tuplas para que queden (tabla,hub) y no (hub,tabla)
		hubs = [hub[::-1] for hub in hubs]
		dirPATH = model_settings.predict_data_path
		files = os.listdir(dirPATH)
		json_files = []
		for file in files:
			if ".json" in file:
				json_files.append(file)
		missing_hubs = []
		#en missing hubs voy a guardar los nombres de los hubs cuyos datos no llegaron
		hubs_dict = {}
		#hubs_dict es un diccionario en que las keys son el nombre de la tabla a la que van a ir los datos
		#y los values son listas con los hubs que van a esa tabla
		for tabla, hub in hubs:
			hubs_dict.setdefault(tabla, []).append(hub)
			if any(hub in file for file in json_files):
				pass
			#si no hay archivos JSON de un Hub que tendria que haber se guarda su nombre en missing_hubs
			else:
				missing_hubs.append(hub)
		if len(missing_hubs) > 0:
			from server_tools import mandar_mail_notificacion
			for hub in missing_hubs:
				print("No llegaron datos de HUB %s"%(hub))

				fecha = time.strftime("%Y%m%d-%H%M%S")
				with open(model_settings.LOG_FILE, "a") as logFile:
					logFile.write("No llegaron datos de %s %s\n"%(hub,fecha))
					mandar_mail_notificacion("No llegaron datos de %s"%(hub), model_settings.notification_mail)
					time.sleep(5)

		for tabla in hubs_dict.keys():
			if any(hub in missing_hubs for hub in hubs_dict[tabla]):
				#si faltan datos de un hub de esta tabla se detiene el proceso para esa tabla
				continue
			# DF va a tener todos los datos obtenidos de los HUBs desde la ultima vez que se corrio este script
			DF = append_entries_json(dirPATH)
			DF_tabla = DF[DF["HUB"].isin(hubs_dict[tabla])]
			columns = hubs_dict[tabla]
			columns.append('MAC')
			columns.append('fechahora')
			columns.append('Zona')
			dataset = pd.DataFrame(columns=columns).astype(np.int)
			dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy crear
			MACS = DF_tabla.MAC.unique()
			print("Empiezo a armar dataset de %s"%(tabla))
			for (index, mac) in enumerate(MACS):
				print("%s/%s"%(index, len(MACS)))
				DF_mac = DF_tabla.loc[DF_tabla['MAC'] == mac].sort_values(by='fechahora')
				for i in range(len(DF_mac) - 1):
					dataset.loc[dataset_i, DF_mac.iloc[i].HUB] = float(DF_mac.iloc[i].RSSI)
					probe_delta = DF_mac.iloc[i + 1].fechahora - DF_mac.iloc[i].fechahora
					if probe_delta < timedelta(seconds=2.5): #aca quiero buscar la lineas que son parte de la misma rafaga de probe request
						pass
					else:
						dataset.loc[dataset_i, 'MAC'] = mac
						dataset.loc[dataset_i, 'fechahora'] = DF_mac.iloc[i].fechahora
						dataset_i += 1
			dataset = dataset.sort_values(by="fechahora")
			#array = dataset.dropna(thresh=6).values
			print("Se armo el dataset de %s"%(tabla))
			array = dataset.values
			X = array[:, 0:(len(dataset.columns) - 3)]
			model = pickle.load(open(model_settings.train_data_path + tabla + "_model.sav", 'rb'))
			Y = model.predict(X)
			#dataset2 = dataset.dropna(thresh=6)
			dataset = dataset.reset_index(drop=True)
			dataset['Zona'] = pd.DataFrame(Y)
			process_and_send(dataset)
			print("Trato de insertar a %s"%(tabla))
			engine = create_engine(model_settings.engine_string)
			dataset.to_sql(tabla, engine, if_exists='append', index=False)
			print("Lo logre")
			for file in json_files:
				for hub in hubs_dict[tabla]:
					if hub in file:
						if not os.path.exists("%s%s"%(model_settings.predict_data_path, tabla)):
							os.makedirs("%s%s"%(model_settings.predict_data_path, tabla))
						command = "mv %s%s %s%s" %(model_settings.predict_data_path, file, model_settings.predict_data_path, tabla)
						print(command)
						os.system(command)
			fecha = time.strftime("%Y%m%d-%H%M%S")
			msg = "Datos procesados y movidos " + fecha + '\n'
			print(msg)
			with open(model_settings.LOG_FILE, "a") as logFile:
				logFile.write(msg)

	except Exception as e:
		fecha = time.strftime("%Y%m%d-%H%M%S")
		error = "Exception predict_and_send: " + str(traceback.format_exc()) + " " + fecha + '\n'
		print(traceback.format_exc())
		with open(model_settings.LOG_FILE, "a") as logFile:
			logFile.write(error)
		from server_tools import mandar_mail_notificacion
		mandar_mail_notificacion(e.message, model_settings.notification_mail)

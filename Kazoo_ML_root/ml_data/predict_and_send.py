import sys
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
import pickle
from xgboost import XGBClassifier
import django
from django.apps import apps

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'Kazoo_ML.settings'
django.setup()

from ml_data.models import hubs_models
ENDPOINT_URL = 'https://api.qa.kazooanalytics.com/api/v2/hub/logs'
def mandar_mail_notificacion(mail_text, To):
	import smtplib
	From = 'kazoohubs@kazoo.com.uy'
	Subject = "Error en servidor ML"
	smtp = smtplib.SMTP('smtp.gmail.com','587')
	smtp.ehlo()
	smtp.starttls()
	smtp.login('kazoohubs@kazoo.com.uy', 'kazooalarmas')
	BODY = '\r\n'.join(['To: %s' % To,
					'From: %s' % From,
                    'Subject: %s' % Subject,
                    '', mail_text])
	smtp.sendmail(From, [To], BODY)
	print ('email sent')

def append_entries_json(dirPATH):
	files = os.listdir(dirPATH)
	files.sort()
	data_cruda = []
	for f in files:
		print(f)
		if ".json" in f:
			with open(os.path.join(dirPATH, f)) as json_file:
				data_cruda.extend(json.loads(json_file.read()))
	DF = pd.DataFrame(data_cruda)
	DF['fechahora'] = pd.to_datetime(DF['fechahora'], format="%Y-%m-%d %H:%M:%S.%f")
	return DF

# esta funcion agarra el dataset, le modifica el formato de la
# informacion y lo envia como la informacion de varios falsos HUB
def process_and_send(dataset):
	def send(reduced_file_data, zona, ENDPOINT):
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
		req = urllib.request.Request(ENDPOINT, compressed_data_to_send)
		req.add_header('Content-Length', '%d' % len(compressed_data_to_send))
		req.add_header('Content-Encoding', 'application/octet-stream')
		response = urllib.request.urlopen(req)
		content = response.read()
		if response.getcode() // 100 == 2: 
			with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'ml_log.log'), "a") as logFile:
				logFile.write("Enviado %s a %s, respuesta: %s\n" % (zona, ENDPOINT, str(response.getcode())))
			print("Enviado %s a %s, respuesta: %s\n" % (zona, ENDPOINT, str(response.getcode())))
			print("Contenido: %s\n" % content)
		else:
			with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'ml_log.log'), "a") as logFile:
				logFile.write("Problemas al mandar %s a %s, respuesta: %s\n" % (zona, ENDPOINT, str(response.getcode())))
	for zona in list(dataset.Zona.unique()):
		if zona == "Afuera":
			continue
		print("Procesando " + zona)
		reduced_file_data = []
		data_zona = dataset[dataset['Zona'] == zona]
		for row in data_zona.itertuples():
			#for column in row:
				#if math.isnan(column):
					#pass
				#else:
					#RSSI = column
					#break
			entry = {'datetime': str(row.fechahora),
					 'mac_phone': row.MAC,
					 'rssi': str(-69)}
			reduced_file_data.append(entry)

		send(reduced_file_data, zona, ENDPOINT_URL)




class TransitionError(Exception):
	def __init__(self, message):
		self.message = message


if __name__ == "__main__":
	try:
		exec_time = time.time()
		hubs = list(hubs_models.objects.values('hub_name', 'hub_ml_model'))
		#hubs es una lista de diccionarios de la forma {'hub_name': '', 'hub_ml_model': ''}
		predict_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"predict_data")
		hubs_dict = {}
		#hubs_dict es un diccionario en que las keys son el nombre de la tabla a la que van a ir los datos
		#y los values son listas con los hubs que van a esa tabla
		for entry in hubs:
			hubs_dict.setdefault(entry["hub_ml_model"], []).append(entry["hub_name"])

		json_files = []
		for file in os.listdir(predict_data_path):
			if ".json" in file:
				json_files.append(file)
		for tabla in hubs_dict.keys():
			# DF va a tener todos los datos que llegaron al servidor desde la ultima vez que se corrio este script
			DF = append_entries_json(predict_data_path)
			# DF_tabla se queda con los datos que pertenecen a un unico modelo
			DF_tabla = DF[DF["HUB"].isin(hubs_dict[tabla])]
			columns = hubs_dict[tabla]
			columns.append('MAC')
			columns.append('fechahora')
			columns.append('Zona')
			# En dataset se van a armar los datos en el formato necesario para pasarselo al modelo
			dataset = pd.DataFrame(columns=columns).astype(np.int)
			dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy crear
			MACS = DF_tabla.MAC.unique()
			print("Empiezo a armar dataset de %s"%(tabla))
			for (index, mac) in enumerate(MACS):
				print("%s/%s"%(index, len(MACS)))
				DF_mac = DF_tabla.loc[DF_tabla['MAC'] == mac].sort_values(by='fechahora')
				for i in range(len(DF_mac) - 1):
					dataset.loc[dataset_i, DF_mac.iloc[i].HUB] = int(DF_mac.iloc[i].RSSI)
					probe_delta = DF_mac.iloc[i + 1].fechahora - DF_mac.iloc[i].fechahora
					if probe_delta < timedelta(seconds=2.5): #aca quiero buscar la lineas que son parte de la misma rafaga de probe request
						pass
					else:
						dataset.loc[dataset_i, 'MAC'] = mac
						dataset.loc[dataset_i, 'fechahora'] = DF_mac.iloc[i].fechahora
						dataset_i += 1
			dataset = dataset.sort_values(by="fechahora")
			dataset.drop(dataset.tail(1).index,inplace=True)
			print("Se armo el dataset de %s"%(tabla))
			array = dataset.values
			X = array[:, 0:(len(dataset.columns) - 3)]
			train_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "train_data")
			model = pickle.load(open(os.path.join(train_data_path, tabla, tabla + "_model.sav"), 'rb'))
			Y = model.predict(X)
			dataset = dataset.reset_index(drop=True)
			dataset['Zona'] = pd.DataFrame(Y)
			process_and_send(dataset)
			print("Trato de insertar a %s"%(tabla))
			Model = apps.get_model("ml_data", tabla)
			Model.objects.bulk_create((Model(**vals) for vals in dataset.to_dict('records')), ignore_conflicts=True)
			print("Lo logre")
			for file in json_files:
				for hub in hubs_dict[tabla]:
					if hub in file:
						if not os.path.exists(os.path.join(predict_data_path, tabla)):
							os.makedirs(os.path.join(predict_data_path, tabla))
						command = "mv %s %s" %(str(os.path.join(predict_data_path, file)), 
												str(os.path.join(predict_data_path, tabla)))
						print(command)
						os.system(command)
			fecha = datetime.now() - timedelta(hours=3)
			msg = "Datos procesados y movidos " + str(fecha) + '\n'
			print(msg)
			with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'ml_log.log'), "a") as logFile:
				logFile.write(msg)
				logFile.write("\nTiempo de ejecucion: %i minutos"%(int((time.time()-exec_time)/60))) 
				logFile.write("\n----------------------------------------------------")

	except Exception as e:
		fecha = time.strftime("%Y%m%d-%H%M%S")
		error = "Exception predict_and_send: " + str(traceback.format_exc()) + " " + fecha + '\n'
		print(traceback.format_exc())
		with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'ml_log.log'), "a") as logFile:
			logFile.write(error)
			logFile.write("\n----------------------------------------------------")
		mandar_mail_notificacion(str(e), "enzo.tng@gmail.com")

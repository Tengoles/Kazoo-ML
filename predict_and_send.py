import sys
from flaskr import model_settings
from datetime import datetime, timedelta
import os
import traceback
import zlib
import urllib.request
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import json
import time
#from sklearn import model_selection
#from sklearn.metrics import classification_report
#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
#from sklearn.model_selection import StratifiedKFold
#from sklearn.model_selection import StratifiedShuffleSplit
import pickle
from xgboost import XGBClassifier

ENDPOINT_URL = 'https://api.kazooanalytics.com/api/v2/hub/logs'

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
        reduced_file_data = []
        print("Procesando " + zona)
        data_zona = dataset[dataset['Zona'] == zona]
        for row in data_zona.itertuples():
            entry = {'datetime': str(row.fechahora),
                     'mac_phone': row.MAC,
                     'rssi': str(-69)} #todo: encontrar un valor mas representativo para este campo
            reduced_file_data.append(entry)

        data_to_send = {
            'hub_identificator': zona,
            'data': reduced_file_data
        }

        print("Enviando " + zona)
        data_to_send = json.dumps(data_to_send)
        print("Comprimiendo")
        compressed_data_to_send = zlib.compress(data_to_send.encode('utf-8'))
        print ('>>> ' + str(sys.getsizeof(data_to_send)))
        print ('>>> ' + str(sys.getsizeof(compressed_data_to_send)))
        req = urllib.request.Request(ENDPOINT_URL, compressed_data_to_send)
        req.add_header('Content-Length', '%d' % len(compressed_data_to_send))
        req.add_header('Content-Encoding', 'application/octet-stream')
        response = urllib.request.urlopen(req)
        content  =  response.read()
        print("Enviado, respuesta: " + str(response.getcode()))

class TransitionError(Exception):
    def __init__(self, message):
        self.message = message
if __name__ == "__main__":
    try:
        dirPATH = model_settings.predict_data_path
        files = os.listdir(dirPATH)
        json_files = []
        for file in files:
            if ".json" in file:
                json_files.append(file)
        for HUB in model_settings.HUBS:
            if any(HUB in file for file in json_files):
                pass
            else:
                print("Faltan datos de %s"%HUB)
                raise TransitionError("Faltan datos de %s"%HUB)
        DF = append_entries_json(dirPATH)    #aca voy a tener en un DF todos los datos obtenidos de los HUBs
                                         #desde la ultima vez que se corrio este script
        #DF = DF.loc[(DF['fechahora'] > "20190411-115300") & (DF['fechahora'] < "20190411-130700")]
        columns = list(DF.HUB.unique())
        columns.append('MAC')
        columns.append('fechahora')
        columns.append('Zona')
        dataset = pd.DataFrame(columns=columns).astype(np.int)
        dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy crear
        MACS = DF.MAC.unique()
        print("Empiezo a armar dataset")
        for mac in MACS:
            DF_mac = DF.loc[DF['MAC'] == mac].sort_values(by='fechahora')
            for i in range(len(DF_mac) - 1):
                dataset.loc[dataset_i, DF_mac.iloc[i].HUB] = float(DF_mac.iloc[i].RSSI)
                probe_delta = DF_mac.iloc[i + 1].fechahora - DF_mac.iloc[i].fechahora
                if probe_delta < timedelta(seconds=2.5): #aca quiero buscar la lineas que son parte de la misma rafaga de probe request
                    pass
                else:
                    dataset.loc[dataset_i, 'MAC'] = mac
                    dataset.loc[dataset_i, 'fechahora'] = DF_mac.iloc[i].fechahora
                    dataset_i += 1

        array = dataset.dropna(thresh=6).values
        X = array[:, 0:(len(dataset.columns) - 3)]
        model = pickle.load(open(model_settings.train_data_path + "finalized_model.sav", 'rb'))
        Y = model.predict(X)
        dataset2 = dataset.dropna(thresh=6)
        dataset2 = dataset2.reset_index(drop = True)
        dataset2['Zona'] = pd.DataFrame(Y)
        dataset2 = dataset2.sort_values(by='fechahora')
        process_and_send(dataset2)
        print("Trato de insertar a DB")
        engine = create_engine(model_settings.engine_string)
        dataset2.to_sql('Sinergia_ML', engine, if_exists='append', index=False)
        print("Lo logre")
        for file in json_files:
            command = "mv %s%s %sprocessed_files" %(model_settings.predict_data_path, file, model_settings.predict_data_path)
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
        mandar_mail_notificacion(e.message,"enzo.tng@gmail.com")

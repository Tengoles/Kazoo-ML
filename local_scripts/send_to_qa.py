import math
import json
import sys
import zlib
import pickle
import urllib.request
from flaskr import model_settings
ENDPOINT_URL = 'https://api.qa.kazooanalytics.com/api/v2/hub/logs'

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
                elif column < 0:
                    RSSI = column
                    break
            entry = {'datetime': str(row.fechahora),
                     'mac_phone': row.MAC,
                     'rssi': str(int(RSSI))}
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
        #with open(model_settings.LOG_FILE, "a") as logFile:
        #	logFile.write("Enviado %s a Kazoo, respuesta: %s\n " % (zona, str(response.getcode())))
        print("Enviado %s a Kazoo, respuesta: %s\n " % (zona, str(response.getcode())))
        print("Contenido: %s\n" % content)
    return data_to_send

dirPATH = model_settings.predict_data_path
dataset = pickle.load(open(dirPATH + 'dataset.pkl', 'rb'))
data_to_send = process_and_send(dataset)
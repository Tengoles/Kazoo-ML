import os
from flaskr import model_settings
from datetime import datetime, timedelta
import json
import pandas as pd
import sys

def load_json_dates(date1, date2, directory):
	date1 = datetime.strptime(date1, '%Y%m%d-%H%M%S') + timedelta(hours=3)
	date2 = datetime.strptime(date2, '%Y%m%d-%H%M%S') + timedelta(hours=3)
	data_directory = model_settings.predict_data_path + directory + "/"
	files = os.listdir(data_directory)
	files.sort()
	data_cruda = []
	for f in files:
		file_date = datetime.strptime(f[0:15],  '%Y%m%d-%H%M%S')
		if (".json" in f and file_date >= date1 and file_date <= date2):
			print(f)
			with open(data_directory + f) as json_file:
				data_cruda.extend(json.loads(json_file.read()))
	DF = pd.DataFrame(data_cruda)
	DF['fechahora'] = pd.to_datetime(DF['fechahora'], format="%Y-%m-%d %H:%M:%S.%f")
	return DF.sort_values(by='fechahora')

cur, conn = model_settings.connect()
try:
	query = """SELECT "MAC", fechahora, "Zona" FROM public."PCSEST" WHERE public."PCSEST".fechahora >= '2019-11-19 00:00:01' AND public."PCSEST".fechahora <= '2019-11-20 00:00:01';"""
	cur.execute(query)
	response = cur.fetchall()
	data = pd.DataFrame(columns=["MAC", "fechahora", "Zona"], data=response)
	cur.close()
	conn.close()
except Exception as e:
	print(e)
	print('hubo error, cierro conexion')
	cur.close()
	conn.close()

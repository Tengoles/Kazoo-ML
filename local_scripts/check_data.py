#Este script hace querys a la tabla de la base de datos que contiene los datos de PCSEST 
#Con esos datos se calculan Visitas totales, visitas recurrentes y visitas unicas. 
#Fue usado para comparar con los calculos que hace el servidor

import os
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
import sys

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="34.196.210.24", database="kazoo", user="kazoo",
                                password="production.K4zoo2018*")

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        #cur.close()
        return cur, conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

cur, conn = connect()
try:
	#query = """SELECT fechahora, mac, rssi, evento FROM public."IPG" WHERE public."IPG".fechahora >= '2019-12-04 00:00:00' AND public."IPG".fechahora <= '2019-12-05 00:00:00';"""
	query = """SELECT "MAC", fechahora, "Zona" FROM public."PCSEST" WHERE public."PCSEST".fechahora >= '2019-12-07 00:00:00' AND public."PCSEST".fechahora <= '2019-12-10 00:00:00';"""
	cur.execute(query)
	response = cur.fetchall()
	data = pd.DataFrame(columns=["MAC", "fechahora", "Zona"], data=response)
	#data = pd.DataFrame(columns=["fechahora", "mac", "rssi", "evento"], data=response)
	data = data[data.Zona == "A2"]
	#data = data[data.evento == "IPG"]
	zonas = data.Zona.unique()
	data.reset_index(inplace=True)
	first_date = datetime(data['fechahora'][0].year, data['fechahora'][0].month, data['fechahora'][0].day, 0, 0)
	last_date = datetime(data['fechahora'][len(data) - 1].year, data['fechahora'][len(data) - 1].month,
						 data['fechahora'][len(data) - 1].day, 0, 0)
	ventana = 600
	print("Ventana de visita recurrente: %s"%ventana)
	macs_recurrentes = []
	for day in range(last_date.day - first_date.day + 1):
		print(str(first_date))
		data_day = data[(data['fechahora'] > first_date) & (data['fechahora'] <= first_date + timedelta(days=1))]
		visitas_unicas = 0
		visitas_totales = 0
		recurrencias = 0
		for zona in zonas:
			print("Zona: %s"%(zona))
			data_zona = data_day[data_day["Zona"] == zona]
			visitas_unicas += len(data_zona.MAC.unique())
			for index, mac in enumerate(data_day.MAC.unique()):
				df_mac = data_zona[data_zona["MAC"] == mac].sort_values(by="fechahora")
				new_mac = True
				for j in range(len(df_mac) - 1):
					probe_delta = df_mac.iloc[j + 1].fechahora - df_mac.iloc[j].fechahora
					if probe_delta > timedelta(seconds=ventana):
						if new_mac == True:
							recurrencias += 1
							macs_recurrentes.append(mac)
							new_mac = False
						visitas_totales += 1
		visitas_totales += visitas_unicas
		print("Visitas unicas: %s \n Visitas totales: %s \nVisitantes recurrentes: %s\n ---------------------" % (str(visitas_unicas),
																								visitas_totales, recurrencias))
		first_date = first_date + timedelta(days=1)
	#for mac in macs_recurrentes:

	cur.close()
	conn.close()
except Exception as e:
	print(e)
	print('hubo error, cierro conexion')
	cur.close()
	conn.close()

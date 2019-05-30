from flaskr import model_settings
from predict_and_send import append_entries_json
import pandas as pd

dirPATH = model_settings.train_data_path
DF = append_entries_json(dirPATH)    #aca voy a tener en un DF todos los datos obtenidos de los HUBs durante el periodo de prueba
MACS = model_settings.MACS
Classes = model_settings.Classes
test_times = model_settings.test_times
print(filtrando entretest_times[0][0][0])
DF_filtrado = DF.loc[(DF['fechahora'] > test_times[0][0][0]) & (DF['fechahora'] < test_times[-1][0][1])]
# las columnas de el dataset van a ser el RSSI en cada Hub, la zona a la que pertenecen esas lecturas y el datetime de cada burst
columns = list(DF_filtrado.HUB.unique())
columns.append('Zona')
columns.append('MAC')
columns.append('fechahora')
DF_filtrado = DF_filtrado[DF_filtrado['MAC'].isin(MACS)]  #solo me interesan los datos obtenidos de estas Macs
dataset = pd.DataFrame(columns=columns).astype(np.int)
dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy creando
print("Empiezo a armar el dataset")
zonas_list = []
for (periodos_zona,zona) in zip(test_times, Classes):
    DF_zona = pd.DataFrame()
    for periodo_zona in periodos_zona:
        #la gracia de esta parte es que tambien funciona con varios periodos de test distintos en una misma zona
        DF_zona = DF_zona.append(DF_filtrado.loc[(DF_filtrado['fechahora'] >= periodo_zona[0]) & (DF_filtrado['fechahora'] <= periodo_zona[1])])
        zonas_list.append(DF_zona)

    for mac in MACS:
        DF_mac = DF_zona.loc[DF_zona['MAC'] == mac].sort_values(by='fechahora') #aca voy a tener un DF con los datos de una de las MAC en el periodo en el que estuvo en una determinada zona
                                                                                #dicha zona es la que esta en 'clase'
        for i in range(len(DF_mac) - 1):
            dataset.loc[dataset_i, DF_mac.iloc[i].HUB] = float(DF_mac.iloc[i].RSSI)
            probe_delta = DF_mac.iloc[i + 1].fechahora - DF_mac.iloc[i].fechahora
            if probe_delta < timedelta(seconds=2.5): #aca quiero buscar la lineas que son parte de la misma rafaga de probe request
                pass
            else:
                dataset.loc[dataset_i, 'Zona'] = zona
                dataset.loc[dataset_i, 'MAC'] = mac
                dataset.loc[dataset_i, 'fechahora'] = DF_mac.iloc[i].fechahora
                dataset_i += 1

import os
import pandas as pd
import json
import numpy as np
from datetime import timedelta
from xgboost.sklearn import XGBClassifier
import pickle
from pathlib import Path
from sklearn.metrics import accuracy_score

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

if __name__ == "__main__":
    train_macs = ["5c:70:a3:0e:28:b2", "14:5a:05:7f:e2:a9", "04:d6:aa:69:da:f1", "18:21:95:c2:4a:1a"]
    Classes = ['E2', 'E1', 'E3','B1', 'A1', 'C1', 'C2', 'A2', 'EURO', 'Afuera']  # estas son las zonas en las cuales quiero que el modelo aprenda que los celulares van
    test_times = [[('20191001-152000', '20191001-154700')],
                [('20191001-154800', '20191001-160500')],
                [('20191001-160730', '20191001-162300')],
                [('20191001-162500', '20191001-164600')],
                [('20191001-164800', '20191001-170300')],
                [('20191001-170600', '20191001-172400')],
                [('20191001-172500', '20191001-173600'), ('20191016-160300', '20191016-161600')],
                [('20191002-110000', '20191002-112200')],
                [('20191002-113000', '20191002-120000')],
                [('20191002-120100', '20191002-123400'), ('20191016-153000', '20191016-154000'), ('20191016-154500', '20191016-155500')]] # rangos de tiempo en los que se realizo cada entrenamiento, uno por cada clase
    print(test_times[-1][-1][1])
    dirPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "PCSEST")
    DF = append_entries_json(dirPATH).sort_values(by="fechahora")
    DF_filtrado = DF.loc[(DF['fechahora'] > test_times[0][0][0]) & (DF['fechahora'] < test_times[-1][-1][1])]
    DF_filtrado = DF_filtrado[DF_filtrado["MAC"].isin(train_macs)]
    # las columnas de el dataset van a ser el RSSI en cada Hub, la zona a la que pertenecen esas lecturas y el datetime de cada burst
    columns = list(sorted(DF_filtrado.HUB.unique()))
    columns.append('Zona')
    columns.append('MAC')
    columns.append('fechahora')
    DF_filtrado = DF_filtrado[DF_filtrado['MAC'].isin(train_macs)]  #solo me interesan los datos obtenidos de estas Macs
    dataset = pd.DataFrame(columns=columns)
    dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy creando
    print("Empiezo a armar el dataset")
    files = os.listdir(dirPATH)
    if 'dataset.pkl' in files:
        #dataset = pickle.load(open(dirPATH + 'dataset.pkl', 'rb'))
        pass
    else:
        for (periodos_zona,zona) in zip(test_times, Classes):
            print("Armando " + str(zona))
            DF_zona = pd.DataFrame()
            for periodo_zona in periodos_zona:
                #la gracia de este for es que tambien funciona con varios periodos de test distintos en una misma zona
                DF_zona = DF_zona.append(DF_filtrado.loc[(DF_filtrado['fechahora'] >= periodo_zona[0]) & (DF_filtrado['fechahora'] <= periodo_zona[1])])

            for mac in train_macs:
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
        #dataset.to_pickle(dirPATH + "dataset.pkl")
    dataset = dataset.sort_values(by='fechahora')
    dataset = dataset.fillna(0)

    X = dataset.iloc[:, 0:dataset.shape[1]-3].values
    Y = dataset.iloc[:, -3].values
    
    model = XGBClassifier()
    """from sklearn.model_selection import LeaveOneOut
    loo = LeaveOneOut()
    accuracies = []
    predictions = []
    for train_index, test_index in loo.split(X):
        print("TRAIN:", train_index, "TEST:", test_index)
        X_train, X_test = X[train_index], X[test_index]
        Y_train, Y_test = Y[train_index], Y[test_index]
        model = model.fit(X_train, Y_train)
        Y_pred = model.predict(X_test)
        accuracy = accuracy_score(Y_test, Y_pred)
        accuracies.append(accuracy)
        predictions.append(Y_pred)
    average = sum(accuracies)/len(accuracies)
    print("Accuracy promedio: %s"%(average))
    dataset["Prediction"] = predictions
    dataset["Accuracy"] = accuracies"""
    final_model = XGBClassifier().fit(X, Y)
    pickle.dump(final_model, open(os.path.join(dirPATH, "PCSEST_model.sav"),'wb'))

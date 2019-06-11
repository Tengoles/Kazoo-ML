from flaskr import model_settings
from predict_and_send import append_entries_json
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from xgboost import XGBClassifier

dirPATH = model_settings.train_data_path
DF = append_entries_json(dirPATH)    #aca voy a tener en un DF todos los datos obtenidos de los HUBs durante el periodo de prueba
MACS = model_settings.MACS
Classes = model_settings.Classes
test_times = model_settings.test_times
print((filtrando entre %s y %s) %(test_times[0][0][0]), test_times[-1][0][1]))
DF_filtrado = DF.loc[(DF['fechahora'] > test_times[0][0][0]) & (DF['fechahora'] < test_times[-1][0][1])]
# las columnas de el dataset van a ser el RSSI en cada Hub, la zona a la que pertenecen esas lecturas y el datetime de cada burst
columns = list(DF_filtrado.HUB.unique())
columns.append('Zona')
columns.append('MAC')
columns.append('fechahora')
DF_filtrado = DF_filtrado[DF_filtrado['MAC'].isin(MACS)]  #solo me interesan los datos obtenidos de estas Macs
dataset = pd.DataFrame(columns=columns).astype(np.int)   #DF vacio donde va a estar el dataset, solo tiene las columnas
print("Empiezo a armar el dataset")
zonas_list = []

#este for va a ir agarrando los datos totales, separandolos por zona.
#se sabe que los datos de cada zona son los que se obtienen al filtrar segun los datetimes en test_times.
#Se va armando el dataset de entrenamiento con los datos de cada zona
dataset_i = 0 #indice de fila para ir recorriendo el dataset final que voy creando
for (periodos_zona,zona) in zip(test_times, Classes):
    DF_zona = pd.DataFrame()
    for periodo_zona in periodos_zona:
        #la gracia de esta parte es que tambien funciona con varios periodos de test distintos en una misma zona
        DF_zona = DF_zona.append(DF_filtrado.loc[(DF_filtrado['fechahora'] >= periodo_zona[0]) & (DF_filtrado['fechahora'] <= periodo_zona[1])])
        zonas_list.append(DF_zona)

    for mac in MACS:
        DF_mac = DF_zona.loc[DF_zona['MAC'] == mac].sort_values(by='fechahora')
        #en DF_mac voy a tener un DF con los datos de una de las MAC en el periodo en el que estuvo en una determinada zona
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
                #no se pasa a otra fila del dataset sin que la diferencia entre dos datos sea mayor a 2.5 segundos

thresh = 6
array = dataset.dropna(thresh=thresh).values #thresh = X: Keep only the rows with at least X non-NA values
X = array[:, 0:(len(dataset.columns) - 3)]  # X va a ser un array teniendo solo los datos de RSSI de cada fila
Y = array[:, (len(dataset.columns) - 3)]  # Y va a tener solamente el dato de Class de cada fila
#model = XGBClassifier().fit(X, Y)
#pickle.dump(model, open("finalized_model.sav",'wb'))
#skf = StratifiedKFold(n_splits=10)
sss = StratifiedShuffleSplit(n_splits=10, test_size=0.20, random_state=5)
# validation_size = 0.2
# seed = 7
# X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size,
#                                                                               random_state=seed)
models = []
for train_index, validation_index in sss.split(X, Y):
    #print("######################")
    X_train, X_validation = X[train_index], X[validation_index]
    Y_train, Y_validation = Y[train_index], Y[validation_index]
    model = XGBClassifier().fit(X_train, Y_train)
    # make predictions for test data
    Y_pred = model.predict(X_validation)
    # evaluate predictions
    accuracy = accuracy_score(Y_validation, Y_pred)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))
    print(confusion_matrix(Y_validation, Y_pred))
    print(classification_report(Y_validation, Y_pred))
     models.append((model, accuracy))
avg_accuracy = sum(list(list(zip(*models)))[1])/len(list(list(zip(*models)))[1])
print("Average Accuracy:  %.2f%%" % (avg_accuracy * 100.0))

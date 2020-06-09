from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pages.models import Page
from django_pandas.io import read_frame
import json
import os
import zlib
import logging
from pathlib import Path
import time
from datetime import datetime, timedelta
from store_json.models import received
from add_hubs.models import hubs
from ml_data.models import hubs_models

#Esta funcion fetchea la informacion de datos recibidos entre dos fechas 
#Luego busca donde hay agujeros de datos y arma un string para mostrarlo en la pagina
def find_missing(date, ml_model):
    date = date.replace(hour=7, minute=30)
    df = read_frame(received.objects.filter(received_datetime__range=(date, date + timedelta(hours=19))), verbose=False)
    hubs_list = read_frame(hubs_models.objects.all(), verbose=False)
    hubs_list = hubs_list[hubs_list.hub_ml_model == ml_model].hub_name
    hubs_list = [hub for hub in hubs_list.values]
    hub_info = ''
    display_info = 'Fecha: %s \n\n\n'%(date.strftime("%d/%m/%Y"))
    if len(df) == 0:
        display_info += "No hay datos en todo el dia de ningun Hub"
    for hub in hubs_list:
        df_temp = df[df.hub_name==hub].sort_values(by="received_datetime")
        missing_data = False
        new_hub = True
        if len(df_temp) == 0:
            hub_info += hub + '\n'
            missing_data = True
            hub_info += "No hay datos en todo el dia\n"
            continue
        elif len(df_temp) == 1:
            hub_info += hub + '\n'
            missing_data = True
            hub_info += "Unico post del dia: %s\n"%(str(df_temp.iloc[0].received_datetime))
            continue
        for i in range(len(df_temp) - 1):
            if i == 0:
                delta = df_temp.iloc[i].received_datetime - date
                if delta > timedelta(minutes=35):
                    #if new_hub == True:
                    hub_info += hub + '\n'
                    new_hub = False
                    missing_data = True
                    hub_info += "Primer archivo del dia: %s"%(str(df_temp.iloc[i].received_datetime)) + '\n'
                    hub_info += "------------\n"
                    continue
            else:
                delta = df_temp.iloc[i+1].received_datetime - df_temp.iloc[i].received_datetime
            if delta > timedelta(minutes=35):
                if new_hub == True:
                    hub_info += hub + '\n'
                    new_hub = False
                missing_data = True
                hub_info += str(df_temp.iloc[i].received_datetime) + '\n'
                hub_info += str(df_temp.iloc[i+1].received_datetime) + '\n'
                hub_info += "------------\n"
        final_datetime = date + timedelta(hours=18)
        delta = final_datetime - df_temp.iloc[len(df_temp)-1].received_datetime
        if delta > timedelta(minutes=40):
            if new_hub == True:
                    hub_info += hub + '\n'
                    new_hub = False
            hub_info += "Ultimo post recibido: "
            hub_info += str(df_temp.iloc[len(df_temp)-1].received_datetime) + '\n'
            missing_data = True
        if missing_data == True:
            #print(df_temp.head())
            #print(df_temp.tail())
            hub_info +=	"#######################\n"
            #print(hub_info)
        missing_data = False
        display_info += hub_info
        hub_info = ''
    return display_info

# Create your views here.
@csrf_exempt
def store_data(request):
    if request.method == "POST":
        try:
            decompressed_data = zlib.decompress(request.body)
            data = json.loads(decompressed_data.decode("UTF-8"))
        except Exception as e:
            data = json.loads(request.body)
        predict_data_path = Path(__file__).parents[2]
        filename = time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json'
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(os.path.dirname(script_path), "ml_data", "predict_data", filename)
        print(file_path)
        with open(file_path, 'a') as fout:
            json.dump(data, fout)
        db_entry = received(received_datetime=datetime.now()-timedelta(hours=3),hub_name=hubs.objects.get(hub_name=data[0]['HUB']))
        db_entry.save()
        return(HttpResponse("Aca se reciben datos en formato JSON"))
    else:
        context = {
        'title': "Datos recibidos",
        'content': "Aqui se va a poder elegir un dia y se va a mostrar los datos que no llegaron en el mismo",
        'page_list': Page.objects.all(),
    }
    return render(request, 'pages/page.html', context)

def display_missing(request, slug):
    ml_model = slug[8:]
    date = datetime.strptime(slug[0:7], "%Y%m%d")
    display_info = find_missing(date, ml_model).replace('\n', '<br>')
    context = {
        'title': "Datos recibidos",
        'content': display_info,
        'page_list': Page.objects.all(),
    }
    return render(request, 'pages/page.html', context)

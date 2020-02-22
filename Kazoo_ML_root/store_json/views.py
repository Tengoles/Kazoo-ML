from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import zlib
import logging
from pathlib import Path
import time
from datetime import datetime, timedelta
from store_json.models import received
from add_hubs.models import hubs

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
        file_path = os.path.join(str(predict_data_path), "predict_data", filename)
        print(file_path)
        with open(file_path, 'a') as fout:
            json.dump(data, fout)
        db_entry = received(received_datetime=datetime.now()-timedelta(hours=3),hub_name=hubs.objects.get(hub_name=data[0]['HUB']))
        db_entry.save()
        return(HttpResponse("Aca se reciben datos en formato JSON"))
    else:
        return(HttpResponse("Aca se reciben datos en formato JSON"))

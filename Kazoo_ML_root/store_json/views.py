from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import zlib
import logging
from pathlib import Path
import time

#logger = logging.getLogger(os.path.join(str(Path(__file__).parents[2]), "logs"), "general_log.log")
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
        return(HttpResponse("Aca se reciben datos en formato JSON"))
    else:
        return(HttpResponse("Aca se reciben datos en formato JSON"))
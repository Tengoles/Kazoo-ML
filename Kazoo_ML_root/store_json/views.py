from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path
import time
# Create your views here.
@csrf_exempt
def store_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        p = Path(__file__).parents[2]
        filename = time.strftime("%Y%m%d-%H%M%S") + "_"  + data['hub'] + '.json'
        print(filename)
        with open(str(p) + filename, 'a') as fout:
            json.dump(data, fout)
        return("Json guardado exitosamente")
    else:
        return(HttpResponse("Imprimime esto"))
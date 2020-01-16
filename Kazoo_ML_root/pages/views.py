from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Totopita preciosa</h1>")

# Create your views here.

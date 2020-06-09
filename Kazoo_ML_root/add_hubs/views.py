from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from pages.models import Page
from django import forms
from django.contrib.auth.decorators import login_required

class add_hub_form(forms.Form):
	hub_name = forms.CharField(required=True)
	hub_ml_model = forms.CharField(required=True)

@login_required
def index(request):
    context = {
            'title': "Agregar Hubs",
            'content': "En esta pagina se van a agregar Hubs a la base de datos con su tabla correspondiente y datetime",
            'last_updated': str(datetime.now()),
            'page_list': Page.objects.all(),
    }
    return render(request, 'pages/page.html', context)

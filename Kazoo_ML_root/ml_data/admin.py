from django.contrib import admin
from .models import ml_models, hubs_models

# Register your models here.
admin.site.register(ml_models)
admin.site.register(hubs_models)
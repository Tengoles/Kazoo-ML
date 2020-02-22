from django.db import models
from add_hubs.models import hubs

# Create your models here.
class ml_models(models.Model):
	model_name = models.CharField(primary_key=True, max_length=50)
	model_file = models.CharField(max_length=50)
	description = models.CharField(max_length=200)

class hubs_models(models.Model):
	hub_name = models.ForeignKey(hubs, on_delete=models.CASCADE, primary_key=True)
	creation_date = models.DateTimeField(auto_now_add=True)
	hub_ml_model = models.ForeignKey(ml_models, on_delete=models.CASCADE)

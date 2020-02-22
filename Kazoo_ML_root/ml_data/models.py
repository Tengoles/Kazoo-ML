from django.db import models
from add_hubs.models import hubs

# Create your models here.
class ml_models(models.Model):
	model_name = models.CharField(primary_key=True, max_length=50)
	model_file = models.CharField(max_length=50)
	description = models.CharField(max_length=200)

class hubs_models(models.Model):
	hub_name = models.ForeignKey(hubs, on_delete=models.CASCADE)
	creation_date = models.DateTimeField(auto_now_add=True)
	hub_ml_model = models.ForeignKey(ml_models, on_delete=models.CASCADE)

class PCSEST(models.Model):
	PCSEST_E2_17 = models.IntegerField(blank=True)
	PCSEST_E2_CRUZADO = models.IntegerField(blank=True)
	PCSEST_E1_MEDIO = models.IntegerField(blank=True)
	PCSEST_E3_ENTRADA = models.IntegerField(blank=True)
	PCSEST_E3_14 = models.IntegerField(blank=True)
	PCSEST_B1_21 = models.IntegerField(blank=True)
	PCSEST_B1_19 = models.IntegerField(blank=True)
	PCSEST_B1_20 = models.IntegerField(blank=True)
	PCSEST_B1_23 = models.IntegerField(blank=True)
	PCSEST_A1_8 = models.IntegerField(blank=True)
	PCSEST_A1_MEDIO = models.IntegerField(blank=True)
	PCSEST_A1_9 = models.IntegerField(blank=True)
	PCSEST_C1_10 = models.IntegerField(blank=True)
	PCSEST_A2_1 = models.IntegerField(blank=True)
	PCSEST_C1_24 = models.IntegerField(blank=True)
	PCSEST_C1_11 = models.IntegerField(blank=True)
	PCSEST_C2_4 = models.IntegerField(blank=True)
	PCSEST_C2_6 = models.IntegerField(blank=True)
	PCSEST_A2_3 = models.IntegerField(blank=True)
	PCSEST_EURO_N1 = models.IntegerField(blank=True)
	PCSEST_EURO_N2 = models.IntegerField(blank=True)
	MAC = models.CharField(max_length=17)
	fechahora = models.DateTimeField()
	Zona = models.CharField(max_length=50)

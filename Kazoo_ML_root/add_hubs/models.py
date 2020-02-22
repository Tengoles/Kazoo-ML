from django.db import models
# Create your models here.

class hubs(models.Model):
	hub_name = models.CharField(primary_key=True, max_length=50)

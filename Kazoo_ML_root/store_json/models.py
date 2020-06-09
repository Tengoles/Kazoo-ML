from django.db import models
from add_hubs.models import hubs

# Create your models here.
class received(models.Model):
	hub_name = models.ForeignKey(hubs, on_delete=models.CASCADE)
	received_datetime = models.DateTimeField()

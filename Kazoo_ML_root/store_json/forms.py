from django import forms
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ml_data.models import ml_models

class Date_Model_Form(forms.Form):
    date = forms.DateField(help_text="YYYY-MM-DD, MM/DD/YYYY, MM/DD/YY")
    model = forms.CharField(help_text="Nombre del modelo del que se quiere ver los datos que llegaron")
    def clean_date(self):
        data = self.cleaned_data['date']
        
        # Check if a date is not in the future. 
        if data > datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Remember to always return the cleaned data.
        return data
    
    def clean_model(self):
        data = self.cleaned_data['model']
        # Check if model is not in the database. 
        if data not in [model.model_name for model in ml_models.objects.all()]:
            raise ValidationError(_('No existe este modelo'))
        
        return data


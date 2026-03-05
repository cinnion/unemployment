from django.forms import CharField, ModelForm
from django import forms

from . import models

class DateInput(forms.DateInput):
    input_type = 'date'


class CreateApplication(ModelForm):
    class Meta:
        model = models.JobApplication
        fields = [
            'when',
            'company',
            'title',
            'posting',
            'confirm',
            'notes',
            'active',
        ]


class EditApplication(ModelForm):
    class Meta:
        model = models.JobApplication
        exclude = ['id']

        widgets =  {
            'when': DateInput(),
            'rejected': DateInput(),
        }

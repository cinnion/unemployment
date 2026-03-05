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

    def __init__(self, *args, **kwargs):
        """
        Make the created_at and updated_at fields read-only.
        """
        super(EditApplication, self).__init__(*args, **kwargs)

        # If the form is bound to an existing instance
        if self.instance and self.instance.pk:
            if 'created_at' in self.fields:
                self.fields['created_at'].widget.attrs['readonly'] = True
                self.fields['created_at'].required = False
                self.fields['created_at'].disabled = True
            if 'updated_at' in self.fields:
                self.fields['updated_at'].widget.attrs['readonly'] = True
                self.fields['updated_at'].required = False
                self.fields['updated_at'].disabled = True

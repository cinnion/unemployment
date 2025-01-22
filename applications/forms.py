from django.forms import CharField, ModelForm

from . import models


class CreateApplication(ModelForm):
    class Meta:
        model = models.JobApplication
        fields = ['when',
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

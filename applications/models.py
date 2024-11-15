from django.db import models

class JobApplication(models.Model):
    when = models.DateField()
    company = models.CharField(max_length=64)
    title = models.CharField(max_length=128, null=True, blank=True)
    posting = models.URLField(null=True)
    confirm = models.URLField(null=True)
    notes = models.CharField(max_length=128, null=True, blank=True)
    active = models.BooleanField(default=True)




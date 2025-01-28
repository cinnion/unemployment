from django.db import models
from django.utils.timezone import now


class JobApplication(models.Model):
    when = models.DateField(default=now, blank=True, db_comment="Date of application.")
    company = models.CharField(max_length=64, db_comment="Name of company.")
    title = models.CharField(max_length=128, blank=True, db_comment="Job title.")
    posting = models.URLField(blank=True, db_comment="URL of job posting, if applicable.")
    confirm = models.URLField(blank=True, db_comment="URL for application confirmation, if applicable.")
    notes = models.CharField(max_length=128, blank=True, db_comment="Notes")
    active = models.BooleanField(default=True, db_comment="Application is still outstanding.")

    class Meta:
        db_table = 'job_applications'

    def __str__(self):
        return '{}: {} @ {}'.format(self.when, self.title, self.company)

# Generated by Django 5.1.3 on 2024-11-15 22:07

import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateField(db_comment='Date of application.', db_default=django.db.models.functions.datetime.Now())),
                ('company', models.CharField(db_comment='Name of company.', max_length=64)),
                ('title', models.CharField(blank=True, db_comment='Job title.', max_length=128)),
                ('posting', models.URLField(blank=True, db_comment='URL of job posting, if applicable.')),
                ('confirm', models.URLField(blank=True, db_comment='URL for application confirmation, if applicable.')),
                ('notes', models.CharField(blank=True, db_comment='Notes', max_length=128)),
                ('active', models.BooleanField(db_comment='Application is still outstanding.', default=True)),
            ],
            options={
                'db_table': 'job_applications',
            },
        ),
    ]

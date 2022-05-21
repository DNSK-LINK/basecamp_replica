# Generated by Django 3.2.13 on 2022-05-10 13:02

import basecamp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basecamp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=255, validators=[basecamp.models.validate_project_title]),
        ),
    ]
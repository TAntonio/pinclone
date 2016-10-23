# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-22 19:29
from __future__ import unicode_literals

import boards.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='slug',
            field=models.CharField(default=boards.models.uuid_generate, max_length=12, unique=True),
        ),
    ]

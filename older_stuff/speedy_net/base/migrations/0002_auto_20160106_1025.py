# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 10:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, default=datetime.date(1916, 1, 31), null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='diet',
            field=models.SmallIntegerField(choices=[(1, 'Vegan'), (2, 'Vegeterian'), (3, 'Carnist')], default=3),
        ),
    ]
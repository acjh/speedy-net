# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-31 03:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190730_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='special_username',
            field=models.BooleanField(default=False, verbose_name='Special username'),
        ),
    ]

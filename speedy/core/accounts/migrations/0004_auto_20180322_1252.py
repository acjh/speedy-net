# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-22 12:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20170727_2009'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entity',
            options={'ordering': ('id',), 'verbose_name': 'entity', 'verbose_name_plural': 'entities'},
        ),
    ]
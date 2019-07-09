# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-09 14:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0027_auto_20190204_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteprofile',
            name='activation_step',
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='activation_step_en',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='siteprofile',
            name='activation_step_he',
            field=models.PositiveSmallIntegerField(default=2),
        ),
    ]
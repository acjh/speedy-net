# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-17 08:40
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations
import speedy.core.models
import speedy.net.accounts.managers


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20161116_0929'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', speedy.net.accounts.managers.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='entity',
            name='id',
            field=speedy.core.models.RegularUDIDField(db_index=True, default=speedy.core.models.generate_regular_udid, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters', regex='[0-9]')], verbose_name='ID'),
        ),
    ]
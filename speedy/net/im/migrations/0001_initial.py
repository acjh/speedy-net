# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-21 11:17
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import speedy.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', speedy.core.models.UDIDField(db_index=True, default=speedy.core.models.generate_id, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters', regex='[0-9]')], verbose_name='ID')),
                ('is_group', models.BooleanField(default=False, verbose_name='is group chat')),
                ('ent1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.Entity', verbose_name='participant 1')),
                ('ent2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.Entity', verbose_name='participant 2')),
                ('group', models.ManyToManyField(to='accounts.Entity', verbose_name='participants')),
            ],
            options={
                'verbose_name': 'chat',
                'ordering': ('-last_message__date_created', '-date_updated'),
                'verbose_name_plural': 'chat',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', speedy.core.models.UDIDField(db_index=True, default=speedy.core.models.generate_id, max_length=20, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='id contains illegal characters', regex='[0-9]')], verbose_name='ID')),
                ('text', models.TextField(verbose_name='message')),
                ('chat', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='im.Chat', verbose_name='chat')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Entity', verbose_name='sender')),
            ],
            options={
                'verbose_name': 'message',
                'get_latest_by': 'date_created',
                'ordering': ('-date_created',),
                'verbose_name_plural': 'messages',
            },
        ),
        migrations.CreateModel(
            name='ReadMark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='im.Chat', verbose_name='chat')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.Entity', verbose_name='entity')),
            ],
            options={
                'verbose_name': 'read mark',
                'get_latest_by': 'date_created',
                'verbose_name_plural': 'read marks',
            },
        ),
        migrations.AddField(
            model_name='chat',
            name='last_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='im.Message', verbose_name='last message'),
        ),
        migrations.AddField(
            model_name='chat',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Site', verbose_name='site'),
        ),
    ]

# Generated by Django 3.0.6 on 2020-06-07 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20200524_1711'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reservedusername',
            options={'ordering': ('username',)},
        ),
    ]

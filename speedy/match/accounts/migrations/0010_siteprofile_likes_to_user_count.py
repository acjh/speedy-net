# Generated by Django 3.1.1 on 2021-02-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_accounts', '0009_siteprofile_profile_picture_months_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteprofile',
            name='likes_to_user_count',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
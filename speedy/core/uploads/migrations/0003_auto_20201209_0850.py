# Generated by Django 3.1.1 on 2020-12-09 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0002_auto_20200607_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='aws_facial_analysis_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='AWS facial analysis time'),
        ),
        migrations.AddField(
            model_name='image',
            name='aws_image_moderation_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='AWS image moderation time'),
        ),
        migrations.AddField(
            model_name='image',
            name='aws_raw_facial_analysis_results',
            field=models.JSONField(blank=True, null=True, verbose_name='AWS raw facial analysis results'),
        ),
        migrations.AddField(
            model_name='image',
            name='aws_raw_image_moderation_results',
            field=models.JSONField(blank=True, null=True, verbose_name='AWS raw image moderation results'),
        ),
        migrations.AddField(
            model_name='image',
            name='number_of_faces',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='number of faces'),
        ),
        migrations.AddField(
            model_name='image',
            name='visible_on_website',
            field=models.BooleanField(default=False, verbose_name='visible on website'),
        ),
    ]

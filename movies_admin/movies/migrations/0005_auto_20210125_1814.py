# Generated by Django 3.1 on 2021-01-25 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_filmwork_video_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmwork',
            name='age_limit',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='возраст'),
        ),
        migrations.AddField(
            model_name='filmwork',
            name='film_creation_date',
            field=models.DateField(blank=True, null=True, verbose_name='дата создания'),
        ),
        migrations.AddField(
            model_name='filmwork',
            name='link',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ссылка'),
        ),
    ]
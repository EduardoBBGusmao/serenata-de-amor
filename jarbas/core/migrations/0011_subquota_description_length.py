# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-24 07:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_extract_receipt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='line',
        ),
        migrations.RemoveField(
            model_name='document',
            name='source',
        ),
        migrations.AlterField(
            model_name='document',
            name='subquota_description',
            field=models.CharField(max_length=128, verbose_name='Subquota descrition'),
        ),
    ]
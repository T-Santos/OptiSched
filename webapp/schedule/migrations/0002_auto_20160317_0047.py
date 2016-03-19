# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='person_max_hours_per_shift',
            field=models.IntegerField(default=8, verbose_name=b'Max Hrs / Shift'),
        ),
        migrations.AlterField(
            model_name='person',
            name='person_max_hours_per_week',
            field=models.IntegerField(default=40, verbose_name=b'Max Hrs / Week'),
        ),
        migrations.AlterField(
            model_name='requirementdatetime',
            name='rqmt_date_date',
            field=models.DateField(verbose_name=b'Effective Date'),
        ),
        migrations.AlterField(
            model_name='requirementdatetime',
            name='rqmt_date_employee_count',
            field=models.PositiveIntegerField(verbose_name=b'Count'),
        ),
        migrations.AlterField(
            model_name='requirementdatetime',
            name='rqmt_date_time',
            field=models.TimeField(verbose_name=b'Effective Time'),
        ),
        migrations.AlterField(
            model_name='requirementdaytime',
            name='rqmt_day_start_time',
            field=models.TimeField(verbose_name=b'Effective Time'),
        ),
    ]
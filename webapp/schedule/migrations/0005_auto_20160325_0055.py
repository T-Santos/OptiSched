# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-25 00:55
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20160321_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='date',
            name='date',
            field=models.DateField(default=datetime.date.today, primary_key=True, serialize=False, verbose_name=b'Date'),
        ),
        migrations.AlterField(
            model_name='date',
            name='date_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='employeetype',
            name='employee_type_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='employeetype',
            name='et_type',
            field=models.CharField(max_length=60, verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='employeetypeshifterror',
            name='employee_type_shift_error_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='employeetypeshifterror',
            name='error_date',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Date', verbose_name=b'Date'),
        ),
        migrations.AlterField(
            model_name='person',
            name='person_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='personemployeetype',
            name='person_employee_type_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='personemployeetype',
            name='pet_employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Person', verbose_name=b'Employee'),
        ),
        migrations.AlterField(
            model_name='personemployeetype',
            name='pet_employee_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.EmployeeType', verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='requestdatetime',
            name='request_date_time_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='requestdatetime',
            name='rqst_date_date',
            field=models.DateField(verbose_name=b'Request Date'),
        ),
        migrations.AlterField(
            model_name='requestdatetime',
            name='rqst_date_employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Person', verbose_name=b'Request Employee'),
        ),
        migrations.AlterField(
            model_name='requestdatetime',
            name='rqst_date_type',
            field=models.CharField(choices=[(b'VACA', b'Vacation'), (b'SICK', b'Sick'), (b'PREF', b'Preferred'), (b'SKIP', b'Cannot Work')], max_length=4, verbose_name=b'Request Type'),
        ),
        migrations.AlterField(
            model_name='requestdaytime',
            name='day_of_week',
            field=models.IntegerField(choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')], verbose_name=b'Day'),
        ),
        migrations.AlterField(
            model_name='requestdaytime',
            name='request_day_time_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='requestdaytime',
            name='rqst_day_employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Person', verbose_name=b'Employee'),
        ),
        migrations.AlterField(
            model_name='requestdaytime',
            name='rqst_day_type',
            field=models.CharField(choices=[(b'PREF', b'Preferred'), (b'SKIP', b'Cannot Work')], max_length=4, verbose_name=b'Request Type'),
        ),
        migrations.AlterField(
            model_name='requirementdatetime',
            name='requirement_date_time_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='requirementdatetime',
            name='rqmt_date_employee_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.EmployeeType', verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='requirementdaytime',
            name='day_of_week',
            field=models.IntegerField(choices=[(0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday'), (6, b'Sunday')], verbose_name=b'Day'),
        ),
        migrations.AlterField(
            model_name='requirementdaytime',
            name='requirement_day_time_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
        migrations.AlterField(
            model_name='requirementdaytime',
            name='rqmt_day_employee_count',
            field=models.PositiveIntegerField(verbose_name=b'Count'),
        ),
        migrations.AlterField(
            model_name='requirementdaytime',
            name='rqmt_day_employee_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.EmployeeType', verbose_name=b'Employee'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Person', verbose_name=b'Employee'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='shift_date',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Date', verbose_name=b'Shift Date'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='shift_employee_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.EmployeeType', verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='shift_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
    ]
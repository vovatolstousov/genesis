# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-06 15:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0008_customuser_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_activity',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 6, 15, 16, 43, 901822, tzinfo=utc)),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-11 10:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0031_verificationcode_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 11, 10, 12, 13, 667843, tzinfo=utc)),
        ),
    ]

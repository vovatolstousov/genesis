# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-13 07:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0043_auto_20170206_0738'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchandise',
            name='seller_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 13, 7, 45, 7, 287933, tzinfo=utc)),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-06 07:38
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0042_auto_20170126_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetwork',
            name='facebook',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='google',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='instagram',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='twitter',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 6, 7, 38, 12, 574933, tzinfo=utc)),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-07 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0009_auto_20161206_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_activity',
            field=models.DateTimeField(),
        ),
    ]
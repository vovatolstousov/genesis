# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-06 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0007_auto_20161206_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.DateField(null=True),
            preserve_default=False,
        ),
    ]

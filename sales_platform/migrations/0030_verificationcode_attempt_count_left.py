# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-11 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0029_auto_20170111_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='verificationcode',
            name='attempt_count_left',
            field=models.IntegerField(default=5),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-21 08:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0010_auto_20161207_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchandise',
            name='video_url',
            field=models.TextField(blank=True),
        ),
    ]

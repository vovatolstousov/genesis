# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-02 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetwork',
            name='facebook',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='google',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='instagram',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='twitter',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]

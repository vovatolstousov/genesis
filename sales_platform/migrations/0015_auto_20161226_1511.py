# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-26 15:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0014_creditcard'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creditcard',
            old_name='seller',
            new_name='owner',
        ),
    ]

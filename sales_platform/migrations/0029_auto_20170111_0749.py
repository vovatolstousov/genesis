# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-11 07:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0028_auto_20170110_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-10 13:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0026_verificationcode_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paytransactions',
            name='payer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payer', to=settings.AUTH_USER_MODEL),
        ),
    ]

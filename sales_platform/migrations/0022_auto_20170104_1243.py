# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-04 12:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0021_paymentcredential'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentcredential',
            old_name='payment',
            new_name='payment_email',
        ),
    ]
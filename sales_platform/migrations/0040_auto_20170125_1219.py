# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-25 12:19
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0039_auto_20170125_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchandise',
            name='preview_photo',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='photo/merchandise/preview_photo', verbose_name='merch_preview_photo'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='preview_photo',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='photo/order_items/preview_photo', verbose_name='orderitem_photo'),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 25, 12, 19, 46, 283382, tzinfo=utc)),
        ),
    ]

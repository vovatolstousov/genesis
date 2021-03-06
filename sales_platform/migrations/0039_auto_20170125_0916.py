# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-25 09:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales_platform', '0038_auto_20170116_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='preview_photo',
            field=models.ImageField(blank=True, null=True, upload_to='photo/order_items/preview_photo', verbose_name='orderitem_photo'),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 25, 9, 16, 44, 172643, tzinfo=utc)),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-23 09:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssserver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trafficlog',
            name='log_date',
            field=models.DateField(auto_now=True, verbose_name='记录日期'),
        ),
    ]

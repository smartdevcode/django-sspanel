# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-19 00:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shadowsocks', '0003_purchasehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlipayRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_code', models.CharField(max_length=64, unique=True, verbose_name='流水号')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='时间')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='金额')),
                ('money_code', models.CharField(max_length=64, unique=True, verbose_name='充值码')),
            ],
            options={
                'verbose_name_plural': '支付宝转账记录',
                'ordering': ('-time',),
            },
        ),
    ]

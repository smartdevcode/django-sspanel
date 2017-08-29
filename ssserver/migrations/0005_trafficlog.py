# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssserver', '0004_auto_20170828_0930'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='节点id')),
                ('upload_traffic', models.BigIntegerField(db_column='u', default=0, verbose_name='上传流量')),
                ('download_traffic', models.BigIntegerField(db_column='d', default=0, verbose_name='下载流量')),
                ('node_id', models.IntegerField(verbose_name='节点id')),
                ('rate', models.FloatField(default=1.0, verbose_name='流量比例')),
                ('traffic', models.CharField(max_length=32, verbose_name='流量记录')),
                ('log_time', models.IntegerField(verbose_name='日志时间')),
            ],
            options={
                'verbose_name_plural': '流量记录',
                'db_table': 'user_traffic_log',
                'ordering': ('-log_time',),
            },
        ),
    ]

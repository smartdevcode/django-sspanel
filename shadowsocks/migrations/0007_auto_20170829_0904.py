# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 01:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shadowsocks', '0006_alipayrequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alipayrequest',
            old_name='usernmae',
            new_name='username',
        ),
    ]

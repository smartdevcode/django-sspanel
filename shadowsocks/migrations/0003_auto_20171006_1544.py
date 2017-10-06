# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shadowsocks', '0002_node_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='method',
            field=models.CharField(choices=[('aes-256-cfb', 'aes-256-cfb'), ('aes-128-ctr', 'aes-128-ctr'), ('rc4-md5', 'rc4-md5'), ('salsa20', 'salsa20'), ('chacha20', 'chacha20'), ('none', 'none')], default='aes-128-ctr', max_length=32, verbose_name='加密类型'),
        ),
        migrations.AlterField(
            model_name='node',
            name='obfs',
            field=models.CharField(choices=[('plain', 'plain'), ('http_simple', 'http_simple'), ('http_simple_compatible', 'http_simple_compatible'), ('http_post', 'http_post'), ('tls1.2_ticket_auth', 'tls1.2_ticket_auth')], default='http_simple', max_length=32, verbose_name='混淆'),
        ),
        migrations.AlterField(
            model_name='node',
            name='protocol',
            field=models.CharField(choices=[('auth_sha1_v4', 'auth_sha1_v4'), ('auth_aes128_md5', 'auth_aes128_md5'), ('auth_aes128_sha1', 'auth_aes128_sha1'), ('auth_chain_a', 'auth_chain_a'), ('origin', 'origin')], default='auth_chain_a', max_length=32, verbose_name='协议'),
        ),
    ]

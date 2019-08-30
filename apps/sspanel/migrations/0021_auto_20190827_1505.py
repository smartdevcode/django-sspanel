# Generated by Django 2.2.1 on 2019-08-27 07:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("sspanel", "0020_auto_20190826_1117")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="level",
            field=models.PositiveIntegerField(
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="用户等级",
            ),
        ),
        migrations.AlterField(
            model_name="vmessnode",
            name="port",
            field=models.IntegerField(default=10086, verbose_name="端口"),
        ),
    ]

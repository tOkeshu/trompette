# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-21 16:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('trompette', '0005_auto_20170521_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 20, 16, 28, 24, 857842, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='status',
            name='boosts',
            field=models.ManyToManyField(related_name='boosts', through='trompette.Boost', to='trompette.Account'),
        ),
    ]

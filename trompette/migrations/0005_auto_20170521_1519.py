# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-21 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trompette', '0004_auto_20170521_1514'),
    ]

    operations = [
        migrations.RenameField('Status', 'boosts2', 'boosts')
    ]

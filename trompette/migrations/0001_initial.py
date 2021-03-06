# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-20 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=500)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='trompette.Account')),
                ('boosts', models.ManyToManyField(related_name='boosts', to='trompette.Account')),
            ],
        ),
    ]

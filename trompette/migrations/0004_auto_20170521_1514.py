# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-21 15:14
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import now
import django.db.models.deletion

def bind_boosts(apps, schema_editor):
    Status  = apps.get_model('trompette', 'Status')
    Boost   = apps.get_model('trompette', 'Boost')

    for status in Status.objects.all():
        for account in status.boosts.all():
            boost = Boost(account=account, status=status, at=now())
            boost.save()

class Migration(migrations.Migration):

    dependencies = [
        ('trompette', '0003_account_following'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at', models.DateTimeField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trompette.Account')),
            ],
        ),
        migrations.AddField(
            model_name='boost',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trompette.Status'),
        ),
        migrations.AddField(
            model_name='status',
            name='boosts2',
            field=models.ManyToManyField(related_name='boosts2', through='trompette.Boost', to='trompette.Account'),
        ),
        migrations.RunPython(bind_boosts, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='status',
            name='boosts',
        ),
    ]

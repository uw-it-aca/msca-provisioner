# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-12 18:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=128)),
                ('changed_by', models.CharField(max_length=32)),
                ('changed_date', models.DateTimeField()),
                ('last_run_date', models.DateTimeField(null=True)),
                ('is_active', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('net_id', models.CharField(max_length=20, unique=True)),
                ('subscription', models.SmallIntegerField(default=0)),
                ('state', models.CharField(choices=[(b'initial', b'Initial'), (b'active', b'Active'), (b'deleted', b'Deleted'), (b'pending', b'Pending'), (b'failed', b'Failed'), (b'disuser', b'Disuser')], max_length=16)),
            ],
        ),
    ]
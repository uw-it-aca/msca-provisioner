# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-13 21:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provisioner', '0002_auto_20160504_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='in_process',
            field=models.NullBooleanField(),
        ),
    ]

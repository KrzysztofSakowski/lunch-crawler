# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-14 18:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0009_alter_user_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facebookpost',
            name='restaurant',
        ),
        migrations.DeleteModel(
            name='FacebookPost',
        ),
    ]

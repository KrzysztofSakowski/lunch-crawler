# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-15 20:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0013_move_database_restaurants'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menubase',
            old_name='restaurant_new',
            new_name='restaurant',
        ),
        migrations.RemoveField(
            model_name='menubase',
            name='restaurant_old',
        ),
    ]

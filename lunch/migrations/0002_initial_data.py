from __future__ import unicode_literals

import os
from django.db import migrations
from collections import namedtuple
from django.contrib.auth import get_user_model


def add_init_data(apps, schema_editor):
    Restaurant = apps.get_model("lunch", "Restaurant")

    RestaurantTuple = namedtuple('RestaurantTuple', ['name', 'facebook_id'])

    restaurants = [
        RestaurantTuple(name="Emalia", facebook_id="543608312506454"),
        RestaurantTuple(name="Welldone", facebook_id="593169484049058"),
        RestaurantTuple(name="Bal", facebook_id="346442015431426"),
        RestaurantTuple(name="Nasze Smaki Bistro", facebook_id="405341849804282"),
        RestaurantTuple(name="PapaYo", facebook_id="477554265603883"),
        RestaurantTuple(name="Mniam", facebook_id="372700889466233"),
    ]

    for restaurant in restaurants:
        model = Restaurant(
            name=restaurant.name,
            facebook_id=restaurant.facebook_id
        )
        model.save()


def remove_init_data(apps, schema_editor):
    Restaurant = apps.get_model("lunch", "Restaurant")
    Restaurant.objects.all().delete()

    FacebookPost = apps.get_model("lunch", "FacebookPost")
    FacebookPost.objects.all().delete()


def create_superuser(apps, schema_editor):
    get_user_model().objects.create_superuser(username='admin', password=os.environ['ADMIN_PASS'], email='admin@example.com')


def delete_superuser(apps, schema_editor):
    user = get_user_model().objects.get(username='admin')
    user.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('lunch', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length')
    ]

    operations = [
        migrations.RunPython(add_init_data, remove_init_data),
        migrations.RunPython(create_superuser, delete_superuser),
    ]

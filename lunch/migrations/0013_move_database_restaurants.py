from __future__ import unicode_literals

from django.db import migrations


def move_objects(apps, schema_editor):
    Restaurant = apps.get_model("lunch", "Restaurant")
    FacebookRestaurant = apps.get_model("lunch", "FacebookRestaurant")
    MenuFacebook = apps.get_model("lunch", "MenuFacebook")

    for restaurant in Restaurant.objects.all():
        facebook_restaurant = FacebookRestaurant(
            name=restaurant.name,
            facebook_id=restaurant.facebook_id
        )

        facebook_restaurant.save()

        query = MenuFacebook.objects.filter(restaurant_old=restaurant)

        for post in query:
            post.restaurant_new.update(restaurant_new=facebook_restaurant)


def remove_temp_restaurant(apps, schema_editor):
    RestaurantBase = apps.get_model("lunch", "RestaurantBase")

    RestaurantBase.objects.get(id=1).delete()


def update_restaurant_ctypes(apps, schema_editor):
    RestaurantBase = apps.get_model("lunch", "RestaurantBase")
    FacebookRestaurant = apps.get_model("lunch", "FacebookRestaurant")
    ContentType = apps.get_model('contenttypes', 'ContentType')

    new_ct = ContentType.objects.get_for_model(FacebookRestaurant)
    RestaurantBase.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=new_ct)


class Migration(migrations.Migration):
    dependencies = [
        ('lunch', '0012_add_polymorphic_restaurant_and_relations')
    ]

    operations = [
        migrations.RunPython(move_objects),
        migrations.RunPython(remove_temp_restaurant),
        migrations.RunPython(update_restaurant_ctypes),
    ]

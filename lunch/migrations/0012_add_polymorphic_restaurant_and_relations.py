# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-15 19:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def remove_user_profile_info(apps, schema_editor):
    UserProfile = apps.get_model("lunch", "UserProfile")

    for user_profile in UserProfile.objects.all():
        user_profile.voted_down_on.clear()
        user_profile.voted_up_on.clear()
        user_profile.restaurants.clear()


def remove_occupation(apps, schema_editor):
    Occupation = apps.get_model("lunch", "Occupation")

    Occupation.objects.all().delete()


def create_temp_restaurant(apps, schema_editor):
    RestaurantBase = apps.get_model("lunch", "RestaurantBase")

    RestaurantBase.objects.create(name="Temp")


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('lunch', '0011_rename_facebook_id_field'),
    ]

    operations = [
        migrations.RunPython(remove_user_profile_info),
        migrations.RunPython(remove_occupation),
        migrations.CreateModel(
            name='RestaurantBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(create_temp_restaurant),
        migrations.RenameField(
            model_name='menubase',
            old_name='restaurant',
            new_name='restaurant_old',
        ),
        migrations.RemoveField(
            model_name='menuemail',
            name='sender_email',
        ),
        migrations.AddField(
            model_name='menuemail',
            name='was_mail_encrypted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='occupation',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lunch.RestaurantBase'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='restaurants',
            field=models.ManyToManyField(to='lunch.RestaurantBase'),
        ),
        migrations.CreateModel(
            name='EmailRestaurant',
            fields=[
                ('restaurantbase_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lunch.RestaurantBase')),
                ('sender_email', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('lunch.restaurantbase',),
        ),
        migrations.CreateModel(
            name='FacebookRestaurant',
            fields=[
                ('restaurantbase_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='lunch.RestaurantBase')),
                ('facebook_id', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('lunch.restaurantbase',),
        ),
        migrations.AddField(
            model_name='restaurantbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='polymorphic_lunch.restaurantbase_set+',
                                    to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='menubase',
            name='restaurant_new',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE,
                                    to='lunch.RestaurantBase'),
            preserve_default=False,
        ),
    ]

from __future__ import unicode_literals

from django.db import migrations


def move_objects(apps, schema_editor):
    FacebookPost = apps.get_model("lunch", "FacebookPost")
    MenuFacebook = apps.get_model("lunch", "MenuFacebook")

    menu_facebook_objects = []

    for facebook_post in FacebookPost.objects.all():
        menu_facebook_objects.append(
            MenuFacebook(
                restaurant=facebook_post.restaurant,
                is_lunch=facebook_post.is_lunch,
                created_date=facebook_post.created_date,
                message=facebook_post.message,
                report_as_not_menu=facebook_post.report_as_not_menu,
                vote_up=facebook_post.vote_up,
                vote_down=facebook_post.vote_down,
                facebook_id=facebook_post.facebook_id,
            )
        )

    for obj in menu_facebook_objects:
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ('lunch', '0007_menu_email_and_facebook')
    ]

    operations = [
        migrations.RunPython(move_objects),
    ]

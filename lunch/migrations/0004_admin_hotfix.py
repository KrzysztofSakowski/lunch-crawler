from django.db import migrations
from django.contrib.auth.models import User

from lunch.models import UserProfile


def create_superuser_profile(apps, schema_editor):
    UserProfile.objects.create(user=User.objects.get(username='admin'))


def delete_superuser_profile(apps, schema_editor):
    user_profile = UserProfile.objects.get(user=User.objects.get(username='admin'))
    user_profile.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('lunch', '0003_userprofile_extension'),
        ('auth', '0008_alter_user_username_max_length')
    ]

    operations = [
        migrations.RunPython(create_superuser_profile, delete_superuser_profile),
    ]

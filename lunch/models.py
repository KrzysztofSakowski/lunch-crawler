from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils.fields import StatusField
from model_utils import Choices


class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    facebook_id = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class FacebookPost(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.deletion.CASCADE)

    STATUS = Choices('confirmed', 'confirmed_not', 'unknown')
    is_lunch = StatusField(db_index=True, default='unknown')

    created_date = models.DateTimeField()
    message = models.TextField()
    report_as_not_menu = models.IntegerField(default=0)
    vote_up = models.IntegerField(default=0)
    vote_down = models.IntegerField(default=0)
    facebook_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        # facebook_id has format: [profile_id]_[post_id]
        # we extract post id
        post_id = self.facebook_id[self.facebook_id.index("_")+1:]

        return f"{self.restaurant.name} {post_id}"


class UserProfile(AbstractUser):
    restaurants = models.ManyToManyField(Restaurant)

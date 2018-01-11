from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField


class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    facebook_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Occupation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.deletion.CASCADE)

    seats_taken = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seats_total = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    date_declared = models.DateField(editable=False)


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
        post_id = self.facebook_id[self.facebook_id.index("_") + 1:]

        return f"{self.restaurant.name} {post_id}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)
    restaurants = models.ManyToManyField(Restaurant)

import logging

from dateutil import parser
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from polymorphic.models import PolymorphicModel
from model_utils import Choices
from model_utils.fields import StatusField

from lunch.facebook_api import FacebookFactory

logger = logging.getLogger("logger")


class RestaurantBase(PolymorphicModel):
    name = models.CharField(max_length=50)

    def crawl_for_menus(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name


class EmailRestaurant(RestaurantBase):
    sender_email = models.CharField(max_length=50, unique=True)

    def crawl_for_menus(self):
        logger.debug(f"{self} crawling for emails from {self.sender_email}")


class FacebookRestaurant(RestaurantBase):
    facebook_id = models.CharField(max_length=50, unique=True)

    def __get_post_ids(self):
        query = MenuFacebook.objects.filter(
            restaurant=self,
        )

        return {post.post_id for post in query}

    def __save_posts(self, posts):
        logger.info(f"For {self}: {len(posts)} posts are going be saved to db")

        for post in posts:
            menu = post['message']
            post_id = post['id']
            created_time = post['created_time']

            date = parser.parse(created_time)

            facebook_post = MenuFacebook(
                restaurant=self,
                created_date=date,
                message=menu,
                post_id=post_id
            )

            try:
                facebook_post.save()
            except IntegrityError:
                logger.warning(f"Facebook post with id={post_id} already exists in db")

    def __str__(self):
        return self.name

    def crawl_for_menus(self, facebook=None):
        if facebook is None:
            facebook = FacebookFactory().create()

        posts = facebook.get_posts(self.facebook_id)

        # filter posts that does not contain message
        posts = [post for post in posts if 'message' in post]

        # filter posts already in db
        ids = self.__get_post_ids()

        posts = [post for post in posts if post['id'] not in ids]

        self.__save_posts(posts=posts)


class Occupation(models.Model):
    restaurant = models.ForeignKey(RestaurantBase, on_delete=models.deletion.CASCADE)

    seats_taken = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seats_total = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    date_declared = models.DateField(editable=False)


class MenuBase(PolymorphicModel):
    restaurant = models.ForeignKey(RestaurantBase, on_delete=models.deletion.CASCADE)

    STATUS = Choices('confirmed', 'confirmed_not', 'unknown')
    is_lunch = StatusField(db_index=True, default='unknown')

    created_date = models.DateTimeField()
    message = models.TextField()
    report_as_not_menu = models.IntegerField(default=0)
    vote_up = models.IntegerField(default=0)
    vote_down = models.IntegerField(default=0)

    def rating(self):
        return self.vote_up - self.vote_down


class MenuFacebook(MenuBase):
    post_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        # facebook_id has format: [profile_id]_[post_id]
        # we extract post id
        post_id_printable = self.post_id[self.post_id.index("_") + 1:]

        return f"{self.restaurant.name} {post_id_printable}"


class MenuEmail(MenuBase):
    was_mail_encrypted = models.BooleanField(default=False)

    def __str__(self):
        return f"Mail: {self.restaurant.name} {self.created_date}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)
    restaurants = models.ManyToManyField(RestaurantBase)

    voted_up_on = models.ManyToManyField(MenuBase, related_name="voted_up_on")
    voted_down_on = models.ManyToManyField(MenuBase, related_name="voted_down_on")

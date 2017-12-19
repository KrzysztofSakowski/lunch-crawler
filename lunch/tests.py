from django.test import TestCase

from collections import namedtuple
from .models import Restaurant, FacebookPost
from django.urls import reverse
import datetime
from .views import find_in_db


class IndexViewTests(TestCase):
    def setUp(self):
        # temporary fix
        # if there is no posts associated with restaurant
        # facebook is going to be crawled and it will fail
        # on travis bc credentials are fake
        Restaurant.objects.filter(pk__gt=1).delete()
        restaurant = Restaurant.objects.get(id=1)

        FacebookPostTuple = namedtuple('FacebookPostTuple', ['restaurant', 'date', 'message', 'is_lunch', 'post_id'])

        posts = [
            FacebookPostTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="1",
                is_lunch="confirmed_not"
            ),
            FacebookPostTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="2",
                is_lunch="unknown"

            ),
            FacebookPostTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="3",
                is_lunch="confirmed"
            ),
            FacebookPostTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="4",
                is_lunch="unknown"
            ),
        ]

        for post in posts:
            facebook_post = FacebookPost(
                restaurant=post.restaurant,
                created_date=post.date,
                message=post.message,
                is_lunch=post.is_lunch,
                facebook_id=post.post_id
            )
            facebook_post.save()

    def test_response(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(200, response.status_code)

    def test_db_find(self):
        restaurant = Restaurant.objects.get(id=1)

        post = find_in_db(restaurant)

        self.assertEqual('3', post.facebook_id)

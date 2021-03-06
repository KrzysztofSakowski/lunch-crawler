import datetime
from collections import namedtuple
from unittest import skip

import dateutil.parser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from .facebook_api import FacebookFactory
from .models import MenuFacebook, UserProfile, RestaurantBase, FacebookRestaurant
from .views import find_in_db
from .apps import LunchConfig


class IndexViewTests(TestCase):

    def tearDown(self):
        LunchConfig.use_facebook_api = True

    def setUp(self):
        # will use facebook stub instead of real API calls
        LunchConfig.use_facebook_api = False

        # temporary fix
        # if there is no posts associated with restaurant
        # facebook is going to be crawled and it will fail
        # on travis bc credentials are fake
        RestaurantBase.objects.filter(pk__gt=2).delete()
        restaurant = RestaurantBase.objects.get(id=2)

        MenuFacebookTuple = namedtuple('MenuFacebookTuple', ['restaurant', 'date', 'message', 'is_lunch', 'post_id'])

        posts = [
            MenuFacebookTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="1",
                is_lunch="confirmed_not"
            ),
            MenuFacebookTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="2",
                is_lunch="unknown"

            ),
            MenuFacebookTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="3",
                is_lunch="confirmed"
            ),
            MenuFacebookTuple(
                restaurant=restaurant,
                date=datetime.date.today(),
                message="",
                post_id="4",
                is_lunch="unknown"
            ),
        ]

        for post in posts:
            facebook_post = MenuFacebook(
                restaurant=post.restaurant,
                created_date=post.date,
                message=post.message,
                is_lunch=post.is_lunch,
                post_id=post.post_id
            )
            facebook_post.save()

    def test_response(self):
        response = self.client.get(reverse("index"))

        # temporary fix while main page redirects
        # self.assertEqual(200, response.status_code)
        self.assertEqual(302, response.status_code)

    def test_db_find(self):
        restaurant = RestaurantBase.objects.get(id=2)

        post = find_in_db(restaurant)

        self.assertEqual("3", post.post_id)

    def test_crawl_for_menus(self):
        test_restaurant = FacebookRestaurant(
            name="text",
            facebook_id="text"
        )
        test_restaurant.save()

        created_time = timezone.now().isoformat()
        message = "text"
        post_id = "543608312506454_764080817125868"

        facebook_stub = FacebookFactory.create(
            created_time=created_time,
            message=message,
            post_id=post_id
        )

        test_restaurant.crawl_for_menus(facebook_stub)

        post_in_db = find_in_db(test_restaurant)

        self.assertEqual(post_id, post_in_db.post_id)
        self.assertEqual(message, post_in_db.message)
        self.assertEqual(dateutil.parser.parse(created_time), post_in_db.created_date)

        test_restaurant.delete()


class FacebookTest(TestCase):
    @skip("Test will not work without facebook credentials")
    def test_is_valid(self):
        facebook = FacebookFactory.create()

        self.assertFalse(facebook.is_valid_profile_id("-1"))
        self.assertTrue(facebook.is_valid_profile_id("372700889466233"))

    @skip("Test will not work without facebook credentials")
    def test_get_id(self):
        facebook = FacebookFactory.create()
        self.assertEqual("1550000475309485", facebook.get_facebook_id("zustdoustkrk"))


class UserProfileTests(TestCase):
    def test_profile_adds_restaurants(self):
        user_profile = UserProfile.objects.create(user=User.objects.create(username='asd', password='1234'))
        restaurant1 = FacebookRestaurant.objects.create(name='Res1', facebook_id='1')
        restaurant2 = FacebookRestaurant.objects.create(name='Res2', facebook_id='2')

        user_profile.restaurants.add(restaurant1)
        user_profile.restaurants.add(restaurant2)

        self.assertEqual(len(user_profile.restaurants.all()), 2)

    def test_profile_validation_for_duplicate_restaurants(self):
        user_profile = UserProfile.objects.create(user=User.objects.create(username='asd', password='1234'))
        restaurant = FacebookRestaurant.objects.create(name='Res1', facebook_id='1')

        user_profile.restaurants.add(restaurant)
        user_profile.restaurants.add(restaurant)

        self.assertEqual(len(user_profile.restaurants.all()), 1)

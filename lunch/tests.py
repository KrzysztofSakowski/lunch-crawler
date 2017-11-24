from django.test import TestCase
from .models import Restaurant
from django.urls import reverse


class TravisTests(TestCase):
    def test_hello_travis(self):
        a = 1
        b = 1

        self.assertEquals(a + b, 2)


class IndexViewTests(TestCase):
    def setUp(self):
        # temporary fix, removing all restaurants from db
        # causes index view to not crawl facebook
        # which cannot be done on travis since facebook
        # credentials are fake
        Restaurant.objects.all().delete()

    def test_response(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)

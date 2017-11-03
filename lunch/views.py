from django.shortcuts import render

from django.conf import settings
import facebook


class Restaurant:
    def __init__(self, name, facebook_name):
        self.name = name
        self.facebook_name = facebook_name


class Menu:
    def __init__(self, name, menu):
        self.name = name
        self.menu = menu


restaurants = [
    Restaurant(name="Emalia", facebook_name="Emaliazablocie"),
    Restaurant(name="Welldone", facebook_name="welldonekrakow"),
    Restaurant(name="Bal", facebook_name="balnazablociu"),
    Restaurant(name="Nasze Smaki Bistoro", facebook_name="405341849804282"),
    Restaurant(name="Nasze Smaki", facebook_name="1451080808450048"),
]

facebook_app_id = getattr(settings, "FACEBOOK_APP_ID", None)
facebook_app_secret = getattr(settings, "FACEBOOK_APP_SECRET", None)

access_token = facebook_app_id + "|" + facebook_app_secret


def index(request):
    graph = facebook.GraphAPI(access_token=access_token)

    menus = []

    for restaurant in restaurants:
        user = restaurant.facebook_name
        profile = graph.get_object(user)
        posts = graph.get_connections(profile['id'], 'posts')

        menu = posts['data'][0]['message']

        menus.append(
            Menu(restaurant.name, menu)
        )

    context = {
        'restaurants': menus
    }

    return render(request, 'lunch/lunch.html', context)

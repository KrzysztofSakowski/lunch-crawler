from django.shortcuts import render

from django.conf import settings
import datetime
import facebook
import dateutil.parser
from dateutil import tz


class Restaurant:
    def __init__(self, name, facebook_name):
        self.name = name
        self.facebook_name = facebook_name


class Menu:
    def __init__(self, name, menu, post_id, created_time, date_str, *, is_today_menu):
        self.name = name
        self.menu = menu
        self.post_id = post_id
        self.created_time = created_time
        self.date_str = date_str
        self.is_today_menu = is_today_menu


restaurants = [
    Restaurant(name="Emalia", facebook_name="Emaliazablocie"),
    Restaurant(name="Welldone", facebook_name="welldonekrakow"),
    Restaurant(name="Bal", facebook_name="balnazablociu"),
    Restaurant(name="Nasze Smaki Bistro", facebook_name="405341849804282"),
    Restaurant(name="Nasze Smaki", facebook_name="1451080808450048"),
    Restaurant(name="PapaYo", facebook_name="papayokrakow"),
    Restaurant(name="Mniam", facebook_name="mniamkrakow"),
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
        post_id = posts['data'][0]['id']
        created_time = posts['data'][0]['created_time']

        date = dateutil.parser.parse(created_time)

        to_zone = tz.gettz('Europe/Warsaw')
        date_polish = date.astimezone(to_zone)

        date_now_polish = datetime.datetime.now()
        date_now_polish = date_now_polish.astimezone(to_zone)

        if restaurant.name == "PapaYo":
            menu = menu.replace("\n\n", "\n")

        is_today_menu = date_polish.day == date_now_polish.day

        menus.append(
            Menu(restaurant.name, menu, post_id, created_time, f"{date_now_polish:%d}", is_today_menu=is_today_menu)
        )

    context = {
        'restaurants': menus
    }

    return render(request, 'lunch/lunch.html', context)

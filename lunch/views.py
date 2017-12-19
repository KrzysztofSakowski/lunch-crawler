from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login

from .models import Restaurant, FacebookPost
from .forms import UserProfileCreationForm

from django.db.utils import IntegrityError

from django.conf import settings
import datetime
import facebook
import dateutil.parser
from dateutil import tz

facebook_app_id = getattr(settings, "FACEBOOK_APP_ID", None)
facebook_app_secret = getattr(settings, "FACEBOOK_APP_SECRET", None)

access_token = facebook_app_id + "|" + facebook_app_secret


def get_facebook_id(graph, facebook_name):
    profile = graph.get_object(facebook_name)
    return profile['id']


def get_menu(restaurant, posts):
    if not posts:
        return None

    post = posts[0]

    menu = post['message']
    post_id = post['id']
    created_time = post['created_time']

    date = dateutil.parser.parse(created_time)

    to_zone = tz.gettz('Europe/Warsaw')
    date_polish = date.astimezone(to_zone)

    date_now_polish = datetime.datetime.now()
    date_now_polish = date_now_polish.astimezone(to_zone)

    if restaurant.name == "PapaYo":
        menu = menu.replace("\n\n", "\n")

    facebook_post = FacebookPost(
        restaurant=restaurant,
        created_date=date,
        message=menu,
        facebook_id=post_id
    )

    try:
        facebook_post.save()
    except IntegrityError:
        print("Menu already in db - can never happen")

    is_today_menu = date_polish.day == date_now_polish.day

    if is_today_menu:
        return facebook_post
    else:
        return None


def find_in_db(restaurant):
    query = FacebookPost.objects.filter(
        restaurant=restaurant,
    )
    query = query.filter(
        created_date__date=datetime.date.today()
    )
    query = query.exclude(
        is_lunch="confirmed_not"
    )

    if query:
        return query[0]
    else:
        return None


def get_post_ids(restaurant):
    query = FacebookPost.objects.filter(
        restaurant=restaurant,
    )

    return {post.facebook_id for post in query}


def crawl_facebook(restaurant):
    graph = facebook.GraphAPI(access_token=access_token)

    posts = graph.get_connections(restaurant.facebook_id, 'posts')['data']

    # filter posts that does not contain message
    posts = [post for post in posts if 'message' in post]

    # filter posts already in db
    ids = get_post_ids(restaurant)

    posts = [post for post in posts if post['id'] not in ids]

    return get_menu(restaurant=restaurant, posts=posts)


def index(request):
    menus = {}

    for restaurant in Restaurant.objects.all():

        menu = find_in_db(restaurant)

        if not menu:
            menu = crawl_facebook(restaurant)

        menus[restaurant] = menu

    context = {
        'menus': menus
    }

    return render(request, 'lunch/lunch.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/')
    else:
        form = UserProfileCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import resolve

from .models import Restaurant, FacebookPost
from .forms import UserProfileCreationForm

from django.db.utils import IntegrityError

import logging

from django.conf import settings
import datetime
import facebook
import dateutil.parser

facebook_app_id = getattr(settings, "FACEBOOK_APP_ID", None)
facebook_app_secret = getattr(settings, "FACEBOOK_APP_SECRET", None)

access_token = facebook_app_id + "|" + facebook_app_secret

logger = logging.getLogger("logger")


def get_facebook_id(graph, facebook_name):
    profile = graph.get_object(facebook_name)
    return profile['id']


def save_posts(restaurant, posts):
    logger.info(f"For {restaurant}: {len(posts)} posts are going be saved to db")

    for post in posts:
        menu = post['message']
        post_id = post['id']
        created_time = post['created_time']

        date = dateutil.parser.parse(created_time)

        facebook_post = FacebookPost(
            restaurant=restaurant,
            created_date=date,
            message=menu,
            facebook_id=post_id
        )

        try:
            facebook_post.save()
        except IntegrityError:
            logger.warning(f"Facebook post with id={post_id} already exists in db")


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
    # this is used to prefer confirmed over unknown
    # taking advantage of their alphabetical order
    query = query.order_by(
        'is_lunch'
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

    save_posts(restaurant=restaurant, posts=posts)


def index_view(request):
    return render(request, 'lunch/index.html')


@login_required(login_url='/login/')
def restaurants_view(request, context=None):
    logger.info("Index requested")

    menus = {}

    if 'example' in resolve(request.path).url_name:
        restaurants = Restaurant.objects.all()
    else:
        restaurants = request.user.restaurants.all()

    for restaurant in restaurants:
        menu = find_in_db(restaurant)

        if not menu:
            crawl_facebook(restaurant)
            menu = find_in_db(restaurant)

        menus[restaurant] = menu

    context = {
        'menus': menus
    }

    return render(request, 'lunch/lunch.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            logger.info(f"user.id")
            return redirect(user)
    else:
        form = UserProfileCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required(login_url='/login/')
def add_restaurant(request):
    return redirect('/')

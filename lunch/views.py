from django.shortcuts import render

from .models import Restaurant, FacebookPost

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


def get_menu(restaurant, posts):
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

    return get_menu(restaurant=restaurant, posts=posts)


def index(request):
    logger.info(f"Index requested")

    menus = {}

    for restaurant in Restaurant.objects.all():

        menu = find_in_db(restaurant)

        if not menu:
            crawl_facebook(restaurant)
            menu = find_in_db(restaurant)

        menus[restaurant] = menu

    context = {
        'menus': menus
    }

    return render(request, 'lunch/lunch.html', context)

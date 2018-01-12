import datetime
import logging
import dateutil.parser
import pandas as pd
from collections import namedtuple

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.db.utils import IntegrityError
from django.shortcuts import redirect, resolve_url
from django.shortcuts import render
from django.urls import reverse
from django.core import serializers
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView

import lunch.forms as lunch_forms
from .facebook_api import FacebookFactory
from .models import Restaurant, FacebookPost, UserProfile, Occupation

logger = logging.getLogger("logger")


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


def crawl_facebook(restaurant, facebook):
    posts = facebook.get_posts(restaurant.facebook_id)

    # filter posts that does not contain message
    posts = [post for post in posts if 'message' in post]

    # filter posts already in db
    ids = get_post_ids(restaurant)

    posts = [post for post in posts if post['id'] not in ids]

    save_posts(restaurant=restaurant, posts=posts)


def calc_avg_occupation(restaurant):
    objs = pd.DataFrame(
        list(Occupation.objects.filter(restaurant=restaurant, date_declared=datetime.datetime.now()).values()))
    if not objs.empty:
        result = namedtuple('seats', ["taken", "total"])
        return result(int(objs['seats_taken'].mean()), int(objs['seats_total'].mean()))
    else:
        return None


def about_view(request):
    return render(request, 'lunch/about.html')


class NotLoggedIn(Exception):
    def __init___(self):
        super(NotLoggedIn, self).__init__(self, "User was not logged in")


class RestaurantsView(TemplateView):
    template_name = 'lunch/lunch_menus.html'
    get_method_log_info = "RestaurantsView view requested"

    def provide_restaurants(self, user=None):
        if user.is_authenticated():
            user_profile = UserProfile.objects.get(user=user)
            restaurants = user_profile.restaurants.all()
        else:
            raise NotLoggedIn

        return restaurants

    def get(self, request, *args, **kwargs):
        logger.info(self.get_method_log_info)

        try:
            restaurants = self.provide_restaurants(request.user)
        except NotLoggedIn:
            return redirect_to_login(
                request.get_full_path(), resolve_url('/login/'), 'next')

        restaurant_contexts = {}

        for restaurant in restaurants:
            menu = find_in_db(restaurant)

            if not menu:
                crawl_facebook(restaurant, FacebookFactory.create())
                menu = find_in_db(restaurant)

            RestaurantContext = namedtuple('RestaurantContext', ["menu", "seats_availability"])
            seats_availability = calc_avg_occupation(restaurant)
            restaurant_contexts[restaurant] = RestaurantContext(menu, seats_availability)

            logger.info(restaurant_contexts[restaurant])

        context = self.get_context_data(**kwargs)
        context['restaurant_contexts'] = restaurant_contexts
        context['seat_form'] = lunch_forms.SeatsOccupiedForm()

        return render(request, self.template_name, context)


class ExampleRestaurantsView(RestaurantsView):
    template_name = 'lunch/lunch_menus.html'
    get_method_log_info = "ExampleRestaurantsView view requested"

    def provide_restaurants(self, user=None):
        return Restaurant.objects.all()


def seats(request):
    seats_form = lunch_forms.SeatsOccupiedForm(request.POST)

    if not request.user.is_authenticated():
        return JsonResponse(data={"error": "login required"},
                            status=400)

    if seats_form.is_valid():
        logger.debug('seats form valid')
        seats_form.save(int(request.POST['restaurant_id']))
        new_availability = calc_avg_occupation(Restaurant.objects.get(id=int(request.POST['restaurant_id'])))
        return JsonResponse(
            data={'seats_taken': new_availability.taken, 'seats_total': new_availability.total,
                  'restaurant_id': request.POST['restaurant_id']})
    else:
        logger.debug('seats form not valid')
        return JsonResponse(data={"error": "form invalid"},
                            status=400)


def signup_view(request):
    if request.method == 'POST':
        form = lunch_forms.UserProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"{user.id}")
            return redirect('restaurants')
    else:
        form = lunch_forms.UserProfileCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required(login_url='/login/')
def add_restaurant_view(request):
    if request.method == 'POST':
        form = lunch_forms.RestaurantAddForm(request.POST)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user=request.user)

            restaurant = form.save(user_profile)
            logger.info(f"{restaurant.name}")
            return redirect(reverse('restaurants'))
    else:
        form = lunch_forms.RestaurantAddForm()

    return render(request, 'lunch/add_restaurant.html', {'form': form})


@staff_member_required
def download_data(request):
    posts = FacebookPost.objects.all()
    data = serializers.serialize('json', posts)

    return JsonResponse(data, safe=False)


def vote(request):
    logger.info("vote view requested")

    if not request.user.is_authenticated():
        return JsonResponse(
            status=400,
            data={"error": "login required to vote"}
        )

    if request.method == 'POST':
        form = lunch_forms.VoteForm(request.POST)

        if form.is_valid():
            context = form.save(request.user)

            if not context["error"]:
                return JsonResponse(context)
            else:
                return JsonResponse(
                    status=400,
                    data=context
                )
        else:
            err_msg = "vote form validation failed"
            logger.warning(err_msg)

            return JsonResponse(
                status=400,
                data={"error": err_msg}
            )

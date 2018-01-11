import datetime
import logging
import dateutil.parser
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


def running_average():
    total = 0.0
    counter = 0
    average = None
    while True:
        term = yield average
        total += term
        counter += 1
        average = total / counter


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


def about_view(request):
    return render(request, 'lunch/about.html')


class restaurants_view(TemplateView):
    template_name = 'lunch/lunch.html'

    def get(self, request, *args, **kwargs):
        logger.info("Index requested")

        if 'example' in resolve(request.path).url_name:
            restaurants = Restaurant.objects.all()
        elif request.user.is_authenticated():

            user_profile = UserProfile.objects.get(user=request.user)

            restaurants = user_profile.restaurants.all()
        else:
            return redirect_to_login(
                request.get_full_path(), resolve_url('/login/'), 'next')

        restaurant_contexts = {}

        for restaurant in restaurants:
            menu = find_in_db(restaurant)

            if not menu:
                crawl_facebook(restaurant, FacebookFactory.create())
                menu = find_in_db(restaurant)

            RestaurantContext = namedtuple('RestaurantContext', ["menu", "seats_availability"])
            try:
                seats_availability = Occupation.objects.get(restaurant=restaurant)
            except ObjectDoesNotExist:
                seats_availability = None
            restaurant_contexts[restaurant] = RestaurantContext(menu, seats_availability)

            logger.info(restaurant_contexts[restaurant])

        context = self.get_context_data(**kwargs)
        context['restaurant_contexts'] = restaurant_contexts
        context['seat_form'] = lunch_forms.SeatsOccupiedForm(self.request.GET or None)

        return self.render_to_response(context)
        # return render(request, 'lunch/lunch.html', context)


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


class seats_taken(FormView):
    success_url = '/'
    template_name = 'lunch/lunch.html'
    form_class = lunch_forms.SeatsOccupiedForm

    def post(self, request, *args, **kwargs):
        seats_form = self.form_class(request.POST)
        if False:# or seats_form.is_valid():
            logger.info('seats form')
            return redirect(self.get_success_url())
        else:
            logger.info('seats form not valid')
            return restaurants_view.as_view()(request)#self.render_to_response(self.get_context_data(seat_form=seats_form))

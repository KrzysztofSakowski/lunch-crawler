from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, validate_email
from django.db.models.functions import datetime
from django.db import IntegrityError, transaction

from .models import UserProfile, Occupation, MenuFacebook, FacebookRestaurant, RestaurantBase, MenuBase, EmailRestaurant
from .facebook_api import Facebook
import logging

logger = logging.getLogger("logger")


def is_valid_profile_id(facebook_id):
    if not Facebook().is_valid_profile_id(facebook_id):
        raise ValidationError("Not valid facebook_id")


class FacebookRestaurantAddForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.fields.TextInput(attrs={
        'placeholder': 'Enter restaurant name',
        'class': 'form-control input-lg',
    }))

    facebook_id = forms.CharField(
        max_length=50,
        widget=forms.fields.TextInput(attrs={
            'placeholder': 'Enter its Facebook id',
            'class': 'form-control input-lg',
        }),
        validators=[is_valid_profile_id]
    )

    error_messages = {
        'name': {'required': "You have to provide name"},
        'facebook_id': {'required': "You have to provide id"}
    }

    form_type = "facebook_form"

    def save(self, user_profile):
        name = self.cleaned_data["name"]
        facebook_id = self.cleaned_data["facebook_id"]

        restaurant = FacebookRestaurant(
            name=name,
            facebook_id=facebook_id
        )

        try:
            restaurant.save()
        except IntegrityError:
            logger.warning(f"Restaurant with id={facebook_id} already exists in db")

        restaurant = FacebookRestaurant.objects.get(facebook_id=facebook_id)

        user_profile.restaurants.add(restaurant)

        return restaurant


class EmailRestaurantAddForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.fields.TextInput(attrs={
        'placeholder': 'Enter restaurant name',
        'class': 'form-control input-lg',
    }))

    sender_email = forms.CharField(
        max_length=50,
        widget=forms.fields.TextInput(attrs={
            'placeholder': 'Enter its e-mail',
            'class': 'form-control input-lg',
        }),
        validators=[validate_email]
    )

    error_messages = {
        'name': {'required': "You have to provide name"},
        'sender_email': {'required': "You have to provide id"}
    }

    form_type = "email_form"

    def save(self, user_profile):
        name = self.cleaned_data["name"]
        sender_email = self.cleaned_data["sender_email"]

        restaurant = EmailRestaurant(
            name=name,
            sender_email=sender_email
        )

        try:
            restaurant.save()
        except IntegrityError:
            logger.warning(f"Restaurant with email={sender_email} already exists in db")

        restaurant = EmailRestaurant.objects.get(sender_email=sender_email)

        user_profile.restaurants.add(restaurant)

        return restaurant


class UserProfileCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserProfileCreationForm, self).save()

        user_profile = UserProfile(user=user)
        user_profile.save()

        return user


class SeatsOccupiedForm(forms.ModelForm):
    class Meta:
        model = Occupation
        fields = ['seats_taken', 'seats_total']

    seats_taken = forms.IntegerField(
        label='Miejsca zajete:',
        widget=forms.fields.NumberInput(attrs={
            'placeholder': 0,
            'class': 'form-control input-lg',
            'default': 0,
        }),
        validators=[MinValueValidator(0)])

    seats_total = forms.IntegerField(
        label='Miejsca ogolem:',
        widget=forms.fields.NumberInput(attrs={
            'placeholder': 0,
            'class': 'form-control input-lg',
            'default': 0,
        }),
        validators=[MinValueValidator(0)])

    def save(self, restaurant_id):
        seats_taken = self.cleaned_data['seats_taken']
        seats_total = self.cleaned_data['seats_total']

        occ = Occupation(restaurant=RestaurantBase.objects.get(id=restaurant_id),
                         seats_taken=seats_taken,
                         seats_total=seats_total,
                         date_declared=datetime.datetime.now())

        occ.save()

        return {'seats': occ}

    def is_valid(self):
        validity = super().is_valid()

        return validity and self.cleaned_data.get('seats_taken', None) <= self.cleaned_data.get('seats_total', None)


class VoteForm(forms.Form):
    menu_id = forms.CharField(
        max_length=50,
        widget=forms.HiddenInput()
    )
    is_up_vote = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )

    @transaction.atomic
    def save(self, user):
        is_up_vote = self.cleaned_data["is_up_vote"]
        menu_id = self.cleaned_data["menu_id"]

        post = MenuBase.objects.get(id=menu_id)
        user_profile = UserProfile.objects.get(user=user)

        context = {
            "error": "",
            "rating": 0
        }

        if is_up_vote:
            if post in user_profile.voted_up_on.all():
                err_msg = f"Already up voted post with id={menu_id}"
                logger.warning(err_msg)
                context["error"] = err_msg

            elif post in user_profile.voted_down_on.all():
                post.vote_up += 1
                post.vote_down -= 1
                user_profile.voted_down_on.remove(post)
                user_profile.voted_up_on.add(post)

            else:
                post.vote_up += 1
                user_profile.voted_up_on.add(post)

        else:
            if post in user_profile.voted_down_on.all():
                err_msg = f"Already down voted post with id={menu_id}"
                logger.warning(err_msg)
                context["error"] = err_msg

            elif post in user_profile.voted_up_on.all():
                post.vote_up -= 1
                post.vote_down += 1
                user_profile.voted_up_on.remove(post)
                user_profile.voted_down_on.add(post)

            else:
                post.vote_down += 1
                user_profile.voted_down_on.add(post)

        post.save()

        context["rating"] = post.rating()

        return context

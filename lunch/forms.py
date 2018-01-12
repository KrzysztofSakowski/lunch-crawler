from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import datetime

from .models import Restaurant, UserProfile, Occupation
from .facebook_api import Facebook
import logging

logger = logging.getLogger("logger")


def is_valid_profile_id(facebook_id):
    if not Facebook().is_valid_profile_id(facebook_id):
        raise ValidationError("Not valid facebook_id")


class RestaurantAddForm(forms.Form):
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

    def save(self, user_profile):
        name = self.cleaned_data["name"]
        facebook_id = self.cleaned_data["facebook_id"]

        restaurant = Restaurant(
            name=name,
            facebook_id=facebook_id
        )

        try:
            restaurant.save()
        except IntegrityError:
            logger.warning(f"Restaurant with id={facebook_id} already exists in db")

        restaurant = Restaurant.objects.get(facebook_id=facebook_id)

        user_profile.restaurants.add(restaurant)

        return restaurant


class FaceBookPostForm(RestaurantAddForm):
    pass


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

    seats_taken = forms.IntegerField(label='Miejsca zajete:', widget=forms.fields.NumberInput(attrs={
        'placeholder': 0,
        'class': 'form-control input-lg',
        'default': 0,
    }))

    seats_total = forms.IntegerField(label='Miejsca ogolem:', widget=forms.fields.NumberInput(attrs={
        'placeholder': 0,
        'class': 'form-control input-lg',
        'default': 0,
    }))

    def save(self, restaurant_id):
        seats_taken = self.cleaned_data['seats_taken']
        seats_total = self.cleaned_data['seats_total']

        occ = Occupation(restaurant=Restaurant.objects.get(id=restaurant_id),
                         seats_taken=seats_taken,
                         seats_total=seats_total,
                         date_declared=datetime.datetime.now())

        occ.save()

        return {'seats': occ }

    def is_valid(self):
        validity = super().is_valid()

        return self.cleaned_data['seats_taken'] <= self.cleaned_data['seats_total'] and validity

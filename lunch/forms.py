from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

from .models import UserProfile, Restaurant


class RestaurantAddForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ('name', 'facebook_id')

        widgets = {
            'name': forms.fields.TextInput(attrs={
                'placeholder': 'Enter restaurant name',
                'class': 'form-control input-lg',
            }),
            'facebook_id': forms.fields.TextInput(attrs={
                'placeholder': 'Enter its Facebook id',
                'class': 'form-control input-lg',
            })
        }

        error_messages = {
            'name': {'required': "You have to provide name"},
            'facebook_id': {'required': "You have to provide id"}
        }

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'facebook_id': ["Restaurant already added"]}
            self._update_errors(e)


class FaceBookPostForm(RestaurantAddForm):
    pass


class UserProfileCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('username',)

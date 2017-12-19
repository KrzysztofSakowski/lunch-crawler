from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserProfileCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('username',)


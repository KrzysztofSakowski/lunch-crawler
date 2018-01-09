from django.conf import settings
from .apps import LunchConfig
import facebook


class FacebookFactory:
    def create(*args, **kwargs):
        if LunchConfig.use_facebook_api:
            return Facebook()
        else:
            return FacebookStub(*args, **kwargs)


class FacebookStub:
    def __init__(self, created_time, message, post_id):
        self._post = {'created_time': created_time,
                      'message': message,
                      'id': post_id}

    def get_posts(self, facebook_id):
        return [
            self._post
        ]


class Facebook:
    def __init__(self):
        facebook_app_id = getattr(settings, "FACEBOOK_APP_ID", None)
        facebook_app_secret = getattr(settings, "FACEBOOK_APP_SECRET", None)

        access_token = facebook_app_id + "|" + facebook_app_secret

        self._graph = facebook.GraphAPI(access_token=access_token)

    def get_posts(self, facebook_id):
        return self._graph.get_connections(facebook_id, 'posts')['data']

    def get_facebook_id(self, facebook_name):
        profile = self._graph.get_object(facebook_name)
        return profile['id']

    def is_valid_profile_id(self, profile_id):
        try:
            self._graph.get_object(profile_id)
            return True
        except facebook.GraphAPIError:
            return False

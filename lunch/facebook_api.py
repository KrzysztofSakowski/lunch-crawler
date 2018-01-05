from django.conf import settings

import facebook


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

from project.settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'lunchcrawler.herokuapp.com',
]

#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True

#X_FRAME_OPTIONS = 'DENY'
#CSRF_COOKIE_HTTPONLY = True

SECURE_SSL_REDIRECT = True

#SECURE_BROWSER_XSS_FILTER = True
#SECURE_CONTENT_TYPE_NOSNIFF = True

# TODO SECURE_HSTS_SECONDS
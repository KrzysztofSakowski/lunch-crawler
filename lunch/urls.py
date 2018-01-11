from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=r'restaurants/example/'), name='index'),
    url(r'^about/$', views.about_view, name='about'),
    url(r'^restaurants/$', views.restaurants_view, name='restaurants'),
    url(r'^restaurants/example/$', views.restaurants_view, name='restaurants_example'),
    url(r'^add_restaurant/$', views.add_restaurant_view, name='add_restaurant'),
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^download/$', views.download_data, name='download'),
    url(r'^vote/$', views.vote, name='vote'),
]

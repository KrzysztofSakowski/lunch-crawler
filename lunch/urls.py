from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^restaurants/$', views.restaurants_view, name='restaurants'),
    url(r'^restaurants/example/$', views.restaurants_view, name='restaurants_example'),
    url(r'^add_restaurant$', views.add_restaurant, name='add_restaurant'),
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]

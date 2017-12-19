from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Restaurant, FacebookPost, UserProfile


class FacebookPostAdmin(admin.ModelAdmin):
    list_display = ('id',       'restaurant', 'format_date', 'is_lunch', 'message')
    list_filter = ('restaurant', 'created_date', 'is_lunch')
    list_editable = ('is_lunch',)

    ordering = ['-created_date']

    def format_date(self, obj):
        return obj.created_date.strftime('%Y-%m-%d, %R')


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'facebook_id')


class UserProfileAdmin(UserAdmin):
    list_display = ('id', 'username')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(FacebookPost, FacebookPostAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

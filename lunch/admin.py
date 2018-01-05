from django.contrib import admin

from .models import Restaurant, FacebookPost, UserProfile


class FacebookPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'format_date', 'is_lunch', 'message')
    list_filter = ('restaurant', 'created_date', 'is_lunch')
    list_editable = ('is_lunch',)

    ordering = ['-created_date']

    def format_date(self, obj):
        return obj.created_date.strftime('%Y-%m-%d, %R')


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'facebook_id')


class UserProfileInline(admin.StackedInline):
    model = UserProfile.restaurants.through


class UserProfileAdmin(admin.ModelAdmin):
    inlines = UserProfileInline,
    list_display = ('name', 'restaurants_list',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserProfileAdmin, self).get_inline_instances(request, obj)

    def name(self, obj):
        return obj.user.username

    def restaurants_list(self, obj):
        return "\n".join([a.name for a in obj.restaurants.all()])

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(FacebookPost, FacebookPostAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

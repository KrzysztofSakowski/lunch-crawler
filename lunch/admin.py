from django.contrib import admin

from .models import MenuFacebook, MenuEmail, UserProfile, Occupation, FacebookRestaurant, EmailRestaurant


class MenuBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'format_date', 'is_lunch', 'message')
    list_filter = ('created_date', 'is_lunch')
    list_editable = ('is_lunch',)

    ordering = ['-created_date']

    def format_date(self, obj):
        return obj.created_date.strftime('%Y-%m-%d, %R')


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


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


class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'seats_taken', 'seats_total', 'date_declared')

    def restaurant(self, obj):
        return obj.restaurant.name


admin.site.register(FacebookRestaurant, RestaurantAdmin)
admin.site.register(EmailRestaurant, RestaurantAdmin)
admin.site.register(MenuFacebook, MenuBaseAdmin)
admin.site.register(MenuEmail, MenuBaseAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Occupation, SeatAdmin)

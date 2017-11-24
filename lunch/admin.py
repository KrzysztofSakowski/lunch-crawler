from django.contrib import admin

from .models import Restaurant, FacebookPost


class FacebookPostAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'format_date', 'is_lunch', 'message')
    list_filter = ('restaurant', 'created_date', 'is_lunch')
    list_editable = ('is_lunch',)

    ordering = ['-created_date']

    def format_date(self, obj):
        return obj.created_date.strftime('%Y-%m-%d, %R')


admin.site.register(Restaurant)
admin.site.register(FacebookPost, FacebookPostAdmin)

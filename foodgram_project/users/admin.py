from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_display_links = ('pk', 'username', 'email')
    search_fields = ('username', 'email')

    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
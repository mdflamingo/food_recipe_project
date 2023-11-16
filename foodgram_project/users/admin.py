from django.contrib import admin

from .models import Follow, User


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = ('user', 'following')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',
                    'first_name', 'last_name', 'email',)
    list_display_links = ('pk', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')

    empty_value_display = '-пусто-'

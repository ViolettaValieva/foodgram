from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import TokenProxy

from .models import Subscribe, User


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админка для пользователя."""

    list_display = ('id', 'full_name', 'username', 'email', 'avatar_tag',
                    'recipe_count', 'subscriber_count', 'is_staff')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = ('id', 'username', 'email', 'full_name')

    @admin.display(description='Имя фамилия')
    def full_name(self, obj):
        """Получение полного имени"""
        return obj.get_full_name()

    @admin.display(description='Аватар')
    def avatar_tag(self, obj):
        """Вывод аватарки пользователя."""
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" '
                             'width="80" height="60">')
        return 'Нет аватара'

    @admin.display(description='Кол-во рецептов')
    def recipe_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def subscriber_count(self, obj):
        """Количество подписчиков."""
        return obj.subscribers.count()


admin.site.register(Subscribe)

admin.site.unregister([Group, TokenProxy])

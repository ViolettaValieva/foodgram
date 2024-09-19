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
    def full_name(self, user):
        """Получение полного имени"""
        return user.get_full_name()

    @admin.display(description='Аватар')
    def avatar_tag(self, user):
        """Вывод аватарки пользователя."""
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" '
                             'width="80" height="60">')
        return 'Нет аватара'

    @admin.display(description='Кол-во рецептов')
    def recipe_count(self, user):
        """Количество рецептов."""
        return user.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def subscriber_count(self, user):
        """Количество подписчиков."""
        return user.followers.count()


admin.site.register(Subscribe)

admin.site.unregister([Group, TokenProxy])

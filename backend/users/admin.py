from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Subscribe, User


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админка для пользователя."""

    list_display = ('id', 'full_name', 'username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = ('id', 'username', 'email', 'full_name')

    @admin.display(description='Имя фамилия')
    def full_name(self, obj):
        """Получение полного имени"""
        return obj.get_full_name()


admin.site.register(Subscribe)

admin.site.unregister([Group, TokenProxy])

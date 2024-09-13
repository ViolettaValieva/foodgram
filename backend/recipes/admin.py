from django.contrib import admin

from core.constants import INGREDIENT_MIN_AMOUNT
from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Строчное представление ингредиента в рецепте."""

    model = RecipeIngredient
    min_num = INGREDIENT_MIN_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка Ингредиентов."""

    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка Тегов."""

    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка Рецептов."""

    list_display = ('name', 'author')
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию рецепта или по автору'
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    readonly_fields = ('in_favorites',)
    empty_value_display = 'Не задано'
    inlines = (RecipeIngredientInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time', 'in_favorites'),
                    'text',
                    'image',
                    'tags',
                )
            },
        ),
    )

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        """Число добавлений этого рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    """Адмика корзины и избранных рецептов."""

    list_display = ('id', 'author', 'recipe')
    list_editable = ('author', 'recipe')

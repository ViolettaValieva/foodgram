from django.contrib import admin
from django.utils.safestring import mark_safe

from core.constants import INGREDIENT_MIN_AMOUNT
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


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

    list_display = ('name', 'author', 'in_favorites',
                    'get_ingredients', 'get_tags', 'image_tag')
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию рецепта или по автору'
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    empty_value_display = 'Не задано'
    inlines = (RecipeIngredientInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time'),
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
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Вывод ингредиентов."""
        return ", ".join([
            f"{ingredient.name} ({ingredient.measurement_unit})"
            for ingredient in obj.ingredients.all()
        ])

    @admin.display(description='Теги')
    def get_tags(self, obj):
        """Вывод тегов."""
        return ", ".join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Картинка')
    def image_tag(self, obj):
        """Отображение изображения рецепта."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="80" height="60" />'
            )
        return 'Нет изображения'


@admin.register(Favorite, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    """Адмика корзины и избранных рецептов."""

    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')

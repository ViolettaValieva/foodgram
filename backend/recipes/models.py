from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (COOKING_MIN_TIME, INGREDIENT_MAX_LENGTH,
                            INGREDIENT_MIN_AMOUNT, MAX_POSITIVE_VALUE,
                            RECIPE_MAX_LENGTH, TAG_MAX_LENGTH,
                            SHORT_URL_MAX_LENGTH)
from core.models import UserRecipeModel
from .services import generate_short_url


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        'Название',
        max_length=INGREDIENT_MAX_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_MAX_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        'Название',
        max_length=TAG_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=TAG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_MAX_LENGTH
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин',
        validators=(
            MinValueValidator(
                COOKING_MIN_TIME,
                message='Минимальное время приготовления - '
                        f'{COOKING_MIN_TIME} мин.'
            ),
            MaxValueValidator(
                MAX_POSITIVE_VALUE,
                message='Максимальное время приготовления - '
                        f'{MAX_POSITIVE_VALUE} мин.'
            ),
        )
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    short_url = models.CharField(
        'Короткая ссылка',
        max_length=SHORT_URL_MAX_LENGTH,
        unique=True,
        blank=True
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = generate_short_url(self.__class__)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель количества ингредиентов для рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(INGREDIENT_MIN_AMOUNT),
            MaxValueValidator(MAX_POSITIVE_VALUE),
        )
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_combination'
            ),
        )

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount},'
                f'{self.ingredient.measurement_unit}')


class Favorite(UserRecipeModel):
    """Модель избранных рецептов."""

    class Meta(UserRecipeModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name


class ShoppingCart(UserRecipeModel):
    """Модель корзины с рецептами."""

    class Meta(UserRecipeModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name

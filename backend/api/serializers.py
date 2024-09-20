from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from core.constants import INGREDIENT_MIN_AMOUNT, MAX_POSITIVE_VALUE
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and user.user_subscriptions.filter(author=obj).exists())


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError('Требуется аватар.')
        return data


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов пользователя."""

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscribeGETSerializer(UserSerializer):
    """Сериализатор для получения подписок [GET]."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                recipes_limit = None
            queryset = queryset[:recipes_limit]
        return SimpleRecipeSerializer(queryset, many=True,
                                      context=self.context).data


class SubscribePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок [POST]."""

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if user.user_subscriptions.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data

    def to_representation(self, instance):
        return SubscribeGETSerializer(instance.author,
                                      context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для получения рецептов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe_ingredients')
    is_favorited = serializers.BooleanField(read_only=True, default=0)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=0)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для создания рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=INGREDIENT_MIN_AMOUNT, max_value=MAX_POSITIVE_VALUE,
        error_messages={
            'min_value': 'Количество ингредиента должно быть не менее '
            f'{INGREDIENT_MIN_AMOUNT}.',
            'max_value': 'Количество ингредиента не может превышать '
            f'{MAX_POSITIVE_VALUE}.'
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all(),
                                              allow_empty=False)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True,
                                                   allow_empty=False)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')

    def validate(self, data):
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError('Требуется указать теги.')

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Теги должны быть уникальными.')

        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError('Требуется указать ингредиенты.')

        ingredient_ids = [
            ingredient['ingredient'].id for ingredient in ingredients
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )

        return data

    def validate_image(self, img):
        if not img:
            raise serializers.ValidationError(
                'У рецепта должно быть изображение.'
            )
        return img

    @staticmethod
    def add_ingredients(recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(recipe=recipe,
                             ingredient=ingredient['ingredient'],
                             amount=ingredient['amount'])
            for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class BaseFavoriteCartSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и корзины покупок."""

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        model = self.Meta.model
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже в {model._meta.verbose_name}.'
            )
        return data

    def to_representation(self, instance):
        return SimpleRecipeSerializer(instance.recipe,
                                      context=self.context).data


class FavoriteSerializer(BaseFavoriteCartSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(BaseFavoriteCartSerializer):
    """Сериализатор для добавления рецептов в корзину покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

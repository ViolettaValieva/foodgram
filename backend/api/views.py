from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import IngredientFilterSet, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShortURLSerializer, SimpleRecipeSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer)
from urlshortener.models import ShortURL
from users.models import Subscribe, User
from core.constants import FILE_NAME
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями, подписками и аватаром."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        if self.action == 'create':
            return UserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """Получение данных текущего пользователя."""
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        queryset = User.objects.filter(subscribe__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Подписка и отписка на пользователя."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request, "author": author}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(
                user=request.user, author=author
            ).first()
            if subscription:
                subscription.delete()
                return Response({'detail': 'Успешная отписка'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Вы не подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Добавление и удаление аватара текущего пользователя."""
        user = request.user
        if request.method == 'PUT':
            if not request.data:
                return Response({'detail': 'Нет данных для обновления.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Аватар не найден.'},
                            status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = SimpleRecipeSerializer(recipe,
                                                data=request.data,
                                                context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(author=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(author=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(author=request.user,
                                               recipe=recipe).first()
            if not favorite:
                return Response(
                    {'errors': 'Рецепт отсутствует в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        """Добавление/удаление рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SimpleRecipeSerializer(recipe,
                                                data=request.data,
                                                context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(
                author=request.user,
                recipe=recipe
            ).exists():
                ShoppingCart.objects.create(author=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(author=request.user,
                                                        recipe=recipe).first()
            if not shopping_cart:
                return Response(
                    {'errors': 'Рецепт отсутствует в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        """Скачивание файла со списком покупок"""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__author=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        file_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total_amount = ingredient['total_amount']
            file_list.append(f'{name} ({measurement_unit}) — {total_amount}')
        file_content = 'Список покупок:\n' + '\n'.join(file_list)
        file = HttpResponse(file_content, content_type='text/plain')
        file['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'
        return file

    @action(detail=True, methods=['get'],
            url_path='get-link')
    def get_link(self, request, pk=None):
        """Формирование короткой ссылки."""
        short_url_instance = ShortURL.objects.get_or_create(
            original_url=request.build_absolute_uri(
                reverse('api:recipes-detail', kwargs={'pk': pk})
            ))[0]
        serializer = ShortURLSerializer(
            short_url_instance, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

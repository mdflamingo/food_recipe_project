from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (CookingRecipe, CookingRecipeIngredient, Favorite,
                            Ingredient, ShoppingList, Tag)
from users.models import Follow, User
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (CookingRecipeListSerializer,
                          CookingRecipesSerializer, FavoriteSerializer,
                          FollowListSerializer, FollowSerializer,
                          IngredientsSerializer, ProfileSerializer,
                          ShoppingListSerializers, TagSerializer)
from .mixins import CreateDeleteMixin


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class CookingRecipeViewSet(viewsets.ModelViewSet):
    """Создание, удаление, изменение, получение рецепта(рецептов).
    Скачивание списка покупок."""

    queryset = CookingRecipe.objects.all()
    serializer_class = CookingRecipesSerializer
    pagination_class = FoodgramPagination
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CookingRecipeListSerializer
        return CookingRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        elif self.action == 'post':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrReadOnlyPermission]
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['get']
    )
    def download_shopping_cart(self, reuest):
        user = reuest.user
        ingredients = (
            CookingRecipeIngredient.objects
            .filter(recipe__recipe_shopping_cart__user=user)
            .values('ingredient')
            .annotate(total_num=Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurement_unit',
                         'total_num'))

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment;'
        'filename="shopping_list.txt"'

        for ingredient in ingredients:
            response.write(
                f'{ingredient[0]}, {ingredient[1]}: {ingredient[2]}\n')

        return response


class FoodgramUserViewSet(UserViewSet):
    """Получение списка подписок."""

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = FoodgramPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(pages, many=True,
                                          context={'request': request})
        return self.get_paginated_response(serializer.data)


class APIFollow(APIView):
    """Подписка и отписка от автора."""

    permission_classes = [IsAuthenticated]
    pagination_class = FoodgramPagination

    def post(self, request, pk):
        user_id = self.request.user.id
        following = get_object_or_404(User, id=pk)

        serializer = FollowSerializer(
            data={'user': user_id, 'following': following.id},
            context={'request': request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)

        follow = Follow.objects.filter(user=user, following=following)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class APIFavorite(CreateDeleteMixin):
    """Добавление рецептов в избранное и удаление из них."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        return self.create_object(
            request, pk,
            FavoriteSerializer)

    def delete(self, request, pk):
        return self.delete_object(
            request, pk, Favorite)


class APIShoppingList(CreateDeleteMixin):
    """Добавление и удаление рецептов из списка покупок."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        return self.create_object(
            request, pk,
            ShoppingListSerializers)

    def delete(self, request, pk):
        return self.delete_object(
            request, pk, ShoppingList)

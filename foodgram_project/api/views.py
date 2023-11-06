from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (CookingRecipe,
                            CookingRecipeIngredient,
                            Favorite,
                            Ingredient,
                            ShoppingList,
                            Tag)
from users.models import Follow, User

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (CookingRecipeListSerializer,
                          CookingRecipesSerializer,
                          FavoriteSerializer,
                          FollowListSerializer,
                          FollowSerializer,
                          IngredientsSerializer,
                          ProfileSerializers,
                          ShoppingListSerializers,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # filter_backends = [IngredientsSerchFilter, ]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    # filter_backends = [IngredientsSerchFilter, ]


class CookingRecipeViewSet(viewsets.ModelViewSet):
    """Создание, удаление, изменение, получение рецепта(рецептов).
    Скачивание списка покупок."""

    queryset = CookingRecipe.objects.all()
    serializer_class = CookingRecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    # filter_backends = [CookingRecipeSearchFilter,]

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
        if not user.shopping_cart.exists():
            return Response({
                'errors': 'Отсутствует список покупок!'
            }, status=status.HTTP_400_BAD_REQUEST)
        ingredients = (
            CookingRecipeIngredient.objects
            .filter(recipe__recipe_shopping_cart__user=reuest.user)
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


class UserViewSet(UserViewSet):
    """Получение списка подписок."""

    queryset = User.objects.all()
    serializer_class = ProfileSerializers

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

    def post(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)

        if user == following:
            return Response({
                'errors': 'Невозможно подписаться на себя!'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, following=following).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, following=following)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)

        if user == following:
            return Response({
                'errors': 'Невозможно отписаться от себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, following=following)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class APIFavorite(APIView):
    """Добавление рецептов в избранное и удаление из них."""

    permission_classes = [IsAuthenticated]
    # может просмтаривать только автор

    def post(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        if Favorite.objects.filter(recipe=recipe).exists():
            return Response({
                'errors': 'Рецепт уже находится в избранном!'},
                status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer(favorite, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        favorite = Favorite.objects.filter(recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class APIShoppingList(APIView):
    """Добавление и удаление рецептов из списка покупок."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        if ShoppingList.objects.filter(recipe=recipe).exists():
            return Response({
                'errors': 'Рецепт добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = ShoppingList.objects.create(user=request.user,
                                                    recipe=recipe)
        serializer = ShoppingListSerializers(shopping_cart,
                                             context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        shopping_cart = ShoppingList.objects.filter(recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                'errors': 'Рецепт не был добавлен в список покупок!'})

from django.http import HttpResponse
from reportlab.pdfgen import canvas

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import filters, status
from djoser.views import UserViewSet
# from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from rest_framework import viewsets

from recipes.models import (CookingRecipe,
                            CookingRecipeIngredient,
                            Tag,
                            Ingredient,
                            Favorite,
                            ShoppingList)
from users.models import User, Follow
from .serializers import (CookingRecipesSerializer,
                          TagSerializer,
                          IngredientsSerializer,
                          CookingRecipeListSerializer,
                          FollowListSerializer,
                          FollowSerializer,
                          ProfileSerializers,
                          FavoriteSerializer,
                          ShoppingListSerializers)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # pagination_class = None
    # permission_classes = (AllowAny,)
    # filter_backends = [IngredientsSerchFilter, ]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    # pagination_class = None
    # permission_classes = (AllowAny,)
    # filter_backends = [IngredientsSerchFilter, ]


class CookingRecipeViewSet(viewsets.ModelViewSet):
    queryset = CookingRecipe.objects.all()
    serializer_class = CookingRecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    #filter_backends = [CookingRecipeSearchFilter,]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CookingRecipeListSerializer
        return CookingRecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     return super().perform_update(serializer)

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
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        for ingredient in ingredients:
            response.write(f'{ingredient[0]}, {ingredient[1]}: {ingredient[2]}\n')

        return response


class UserViewSet(UserViewSet):
    """Список подписок."""
    # добавить пагинацию и затестить эндопойнт моих подписок
    #добавить фильтры и затестить эндпойнты
    # serializer_class = FollowListSerializer
    # pagination_class = LimitOffsetPagination

    # def get_queryset(self):
    #     return User.objects.filter(following__user=self.request.user)
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
        serializer = FollowListSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class APIFollow(APIView):
    """Подписка и отписка от автора"""
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
    """добавленпе рецертов в избранное"""
    permission_classes = [IsAuthenticated] # может просмтаривать только автор

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
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        if ShoppingList.objects.filter(recipe=recipe).exists():
            return Response({
                'errors': 'Рецепт добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = ShoppingList.objects.create(user=request.user, recipe=recipe)
        serializer = ShoppingListSerializers(shopping_cart, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(CookingRecipe, id=pk)
        shopping_cart = ShoppingList.objects.filter(recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                'errors': 'Рецепт не добавлен в список покупок!'})
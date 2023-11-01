from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import filters, status
from djoser.views import UserViewSet
# from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from rest_framework import viewsets

from recipes.models import CookingRecipe, Tag, Ingredient
from users.models import User, Follow
from .serializers import (CookingRecipesSerializer,
                          TagSerializer,
                          IngredientsSerializer,
                          CookingRecipeListSerializer,
                          FollowListSerializer,
                          FollowSerializer,
                          ProfileSerializers)


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


class UserViewSet(UserViewSet):
    # добавить пагинацию и затестить эндопойнт моих подписок
    #добавить фильтры и затестить эндпойнты
    # serializer_class = FollowListSerializer
    # pagination_class = LimitOffsetPagination

    # def get_queryset(self):
    #     return User.objects.filter(following__user=self.request.user)
    queryset = User.objects.all()
    serializer_class = ProfileSerializers
    pagination_class = LimitOffsetPagination

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )
    # def subscribe(self, request, **kwargs):
    #     user = request.user
    #     author_id = self.kwargs.get('id')
    #     following = get_object_or_404(User, id=author_id)

    #     if request.method == 'POST':
    #         serializer = FollowSerializer(following,
    #                                       data=request.data,
    #                                       context={"request": request})
    #         print(f'!!!!{serializer}')
    #         serializer.is_valid(raise_exception=True)

    #         Follow.objects.create(user=user, following=following)

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     if request.method == 'DELETE':
    #         subscription = get_object_or_404(Follow,
    #                                          user=user,
    #                                          following=following)
    #         subscription.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

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


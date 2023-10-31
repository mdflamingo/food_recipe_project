from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status
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
                          FollowSerializer)


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


class FollowListView(ListAPIView):
    # добавить пагинацию и затестить эндопойнт моих подписок
    #добавить фильтры и затестить эндпойнты
    serializer_class = FollowListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
        # current_user = self.request.user # Предполагается, что текущий пользователь авторизован
        # limit = self.request.query_params.get('limit') # Получить количество объектов на странице
        # print(limit)
        # recipes_limit = self.request.query_params.get('recipes_limit') # Получить количество объектов внутри поля recipes

        # following_users = current_user.following_users.all()

        # # Ограничение количества объектов внутри поля recipes
        # if recipes_limit:
        #     following_users = following_users.prefetch_related('recipes')[:int(recipes_limit)]

        # return following_users


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



# def subscription()
    

# def unsubscribe()

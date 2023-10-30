from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView

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
    pagination_class = None
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
    serializer_class = FollowListSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class APIFollow(APIView):
    def post(self, request, pk):
        # serializer = FollowSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED) 
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        user = request.user
        following = get_object_or_404(User, id=pk)

        if user == following:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
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
        # post.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

        if user == following:
            return Response({
                'errors': 'Вы не можете отписываться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, following=following)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



# def subscription()
    

# def unsubscribe()

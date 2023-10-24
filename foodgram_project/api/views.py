from rest_framework.response import Response
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
                          FollowListSerializer)


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
    serializer_class = FollowListSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

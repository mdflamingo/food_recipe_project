from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import viewsets

from recipes.models import CookingRecipe, Tag, Ingredients
from .serializers import CookingRecipesSerializer, TagSerializer, IngredientsSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer(many=True)
    # pagination_class = None
    # permission_classes = (AllowAny,)
    # filter_backends = [IngredientsSerchFilter, ]


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    # pagination_class = None
    # permission_classes = (AllowAny,)
    # filter_backends = [IngredientsSerchFilter, ]


class CookingRecipeViewSet(viewsets.ModelViewSet):
    queryset = CookingRecipe.objects.all()
    serializer_class = CookingRecipesSerializer

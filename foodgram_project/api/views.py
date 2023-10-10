from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import viewsets
from djoser.views import UserViewSet
# from djoser.serializers import UserSerializer


from recipes.models import CookingRecipe, Tag, Ingredients
from users.models import User
from .serializers import CookingRecipesSerializer, TagSerializer, IngredientsSerializer, UserSerializer


class CookingRecipeViewSet(viewsets.ModelViewSet):
    queryset = CookingRecipe.objects.all()
    serializer_class = CookingRecipesSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer(many=True)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # @action(
    #     detail=False,
    #     methods=("get",),
    #     permission_classes=(IsAuthenticated,),
    # )
    # def me(self, request):
    #     serializer = UserSerializer(
    #         request.user, data=request.data
    #     )
    #     if not serializer.is_valid():
    #         return Response(
    #             serializer.errors, status=status.HTTP_400_BAD_REQUEST
    #         )
    #     # if request.method == "PATCH":
    #     #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)

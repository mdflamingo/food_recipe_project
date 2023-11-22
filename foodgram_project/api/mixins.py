from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import CookingRecipe


class CreateDeleteMixin(APIView):
    """Добавление и удаление рецептов в ."""

    def create_object(self, request, pk, serializer_class):
        user = request.user
        try:
            recipe = get_object_or_404(CookingRecipe, id=pk)
        except Http404:
            return Response({'errors': 'Рецепт не существует!'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_class(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': self.request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, request, pk, model_class):
        user = request.user
        try:
            recipe = get_object_or_404(CookingRecipe, id=pk)
        except Http404:
            return Response({'errors': 'Рецепт не существует!'},
                            status=status.HTTP_404_NOT_FOUND)
        instance = model_class.objects.filter(user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

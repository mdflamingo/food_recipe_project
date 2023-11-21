from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateDeleteMixin(APIView):
    """Добавление и удаление рецептов в ."""

    def create_object(self, user, recipe, serializer_class, model_class):
        serializer = serializer_class(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': self.request})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def delete_object(self, user, recipe, model_class):
        instance = model_class.objects.filter(user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

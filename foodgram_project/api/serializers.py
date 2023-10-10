from rest_framework import serializers
from djoser.serializers import UserSerializer

from recipes.models import CookingRecipe, Tag, Ingredients
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('color', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("email", "id", "username", "first_name", "last_name")

# class CustomUserSerializer(UserSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'username', 'first_name', 'last_name')
class CookingRecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientsSerializer(many=True)

    class Meta:
        model = CookingRecipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time', )
from rest_framework import serializers
from djoser.serializers import UserSerializer

from recipes.models import CookingRecipe, Tag, Ingredients
from users.models import User


class CookingRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingRecipe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


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

from rest_framework import serializers

from recipes.models import CookingRecipe, Tag, Ingredients
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('color', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measure_unit',)


class CookingRecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientsSerializer(many=True)

    class Meta:
        model = CookingRecipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time', )


class ProfileSerializers(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name',
                  'is_subscribed')
        
    def get_is_subscribed(self, obj):
        return False
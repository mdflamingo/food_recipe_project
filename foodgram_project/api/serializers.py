import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (CookingRecipe,
                            CookingRecipeIngredient,
                            Favorite,
                            Ingredient,
                            ShoppingList,
                            Tag)
from users.models import Follow, User


class ProfileSerializers(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed')

    # def get_is_subscribed(self, obj):
    #     # print(obj)
    #     # if not self.context["request"].user.pk:
    #     #     return None
    #     # else:
    #     #     user = self.context['request'].user
    #     print(self.context)
    #     return bool(obj.following.filter(user=request.user))
    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Follow.objects.filter(user=user, following=obj).exists()
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated and bool(obj.following.filter(user=user)))


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ReadCookingRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = CookingRecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = CookingRecipeIngredient
        fields = ('id', 'amount')


class CookingRecipeListSerializer(serializers.ModelSerializer):
    # получение рецепта GET
    ingredients = ReadCookingRecipesSerializer(
        many=True,
        source='ingredient_used')
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializers(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = CookingRecipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).exists()


class CookingRecipesSerializer(serializers.ModelSerializer):
    # cоздание рецепта
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = AddIngredientsSerializer(
        many=True)
    # source='ingredient_used')
    image = Base64ImageField()

    class Meta:
        model = CookingRecipe
        fields = ('ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time',
                  )

    def validate(self, data):
        tags = data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        ingredients_id = [el.get('id') for el in ingredients]

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Выберите тег!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'})
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Невозможно создать рецепт без ингредиентов!'})
        if len(ingredients) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться!'})

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = CookingRecipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = ingredient.get('id')
            current_amount = ingredient.get('amount')
            recipe.ingredients.add(
                current_ingredient,
                through_defaults={
                    'amount': current_amount,
                }
            )
            for tag in tags:
                recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_used')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        instance.tags.clear()

        for tag in tags:
            instance.tags.add(tag)

        instance.ingredients.clear()

        for ingredient in ingredients:
            current_ingredient = ingredient.get('id')
            current_amount = ingredient.get('amount')
            instance.ingredients.add(
                current_ingredient,
                through_defaults={
                    'amount': current_amount,
                }
            )
        instance.save()

        return instance

    def to_representation(self, instance):
        return CookingRecipeListSerializer(instance, context=self.context).data


class ReducedRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = CookingRecipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FollowListSerializer(serializers.ModelSerializer):
    # список подписок
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = CookingRecipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
        return ReducedRecipeSerializers(queryset, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated and bool(obj.subscriber.filter(user=user)))

    def get_recipes_count(self, obj):
        return CookingRecipe.objects.filter(author=obj).count()


class FollowSerializer(serializers.ModelSerializer):
    # создание подписки

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.following,
            context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ReducedRecipeSerializers(
            instance.recipe,
            context=self.context).data


class ShoppingListSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ReducedRecipeSerializers(
            instance.recipe,
            context=self.context).data

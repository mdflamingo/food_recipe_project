from rest_framework import serializers

from recipes.models import (CookingRecipe, CookingRecipeIngredient, Favorite,
                            Ingredient, ShoppingList, Tag)
from users.models import Follow, User
from .fields import Base64ImageField, Hex2NameColor


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class ReadCookingRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

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
    """Сериализатор для добавления ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = CookingRecipeIngredient
        fields = ('id', 'amount')


class CookingRecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка рецептов или рецепта."""

    ingredients = ReadCookingRecipesSerializer(
        many=True,
        source='ingredient_used')
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')

    class Meta:
        model = CookingRecipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj).exists()


class CookingRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или изменения рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = AddIngredientsSerializer(
        many=True)
    image = Base64ImageField()

    class Meta:
        model = CookingRecipe
        fields = ('ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time',
                  )

    def validate(self, data):
        if not data.get('tags'):
            raise serializers.ValidationError(
                {'tags': 'Выберите тег!'})
        if len(data.get('tags')) != len(set(data.get('tags'))):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'})
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Невозможно создать рецепт без ингредиентов!'})

        ingredients_id = [el.get('id') for el in data.get('ingredients')]

        if len(data.get('ingredients')) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться!'})

        return data

    def create_ingredients(self, ingredients, recipe):
        data = []
        for ingredient in ingredients:
            current_ingredient = ingredient.get('id')
            current_amount = ingredient.get('amount')
            object = CookingRecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=current_amount)

            data.append(object)

        return CookingRecipeIngredient.objects.bulk_create(data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = CookingRecipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)

        for tag in tags:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        super().update(instance, validated_data)

        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)

        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.save()

        return instance

    def to_representation(self, instance):
        return CookingRecipeListSerializer(instance, context=self.context).data


class ReducedRecipeSerializers(serializers.ModelSerializer):
    """Урезанный сериализатор рецепта."""

    class Meta:
        model = CookingRecipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FollowListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка подписок."""

    recipes = serializers.SerializerMethodField(
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

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
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

    def get_recipes_count(self, obj):
        return CookingRecipe.objects.filter(author=obj).count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на автора."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        user = data.get('user')
        following = data.get('following')

        if user == following:
            raise serializers.ValidationError({
                'errors': 'Невозможно подписываться и отписываться от себя!'})

        if not User.objects.filter(id=following.id).exists():
            raise serializers.ValidationError({
                'errors': 'Пользователь не существует!'})

        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.following,
            context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт добавлен в избранное!'
            })
        return data

    def to_representation(self, instance):
        return ReducedRecipeSerializers(
            instance.recipe,
            context=self.context).data


class ShoppingListSerializers(serializers.ModelSerializer):
    """Сериализатор для получения списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')

        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт добавлен в список покупок!'
            })
        return data

    def to_representation(self, instance):
        return ReducedRecipeSerializers(
            instance.recipe,
            context=self.context).data

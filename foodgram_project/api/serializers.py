from rest_framework import serializers

from recipes.models import CookingRecipe, Tag, Ingredients, CookingRecipeIngredients
from users.models import User


class ProfileSerializers(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'color', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measure_unit',)


class ReadCookingRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measure_unit = serializers.ReadOnlyField(source='ingredient.measure_unit')

    class Meta:
        model = CookingRecipeIngredients
        fields = ('id', 'name', 'measure_unit', 'amount')


class AddIngredientsSerializers(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = CookingRecipeIngredients
        fields = ('id', 'amount')


class CookingRecipeListSerializer(serializers.ModelSerializer):
    # получение рецепта GET
    ingredients = ReadCookingRecipesSerializer(many=True,
                                               source='recipe_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializers()

    class Meta:
        model = CookingRecipe
        field = ('ingredients', 'author', 'is_favorited',
                 'is_in_shopping_cart',
                 'name', 'image', 'text', 'cooking_time')


class CookingRecipesSerializer(serializers.ModelSerializer):
    # cоздание рецепта
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientsSerializers(many=True)

    class Meta:
        model = CookingRecipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time',
                  'image')

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({'tags': 'Выберите тег!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги не должны повторяться'})
        return data

    # добавить валидацию ингредиентов, игредиеты не должны повторятьсяю
    # реализовать уникальность ингредиентов на уровне класса
    # unique_together = ("name", "measurement_unit") в Meta

    def create(self, validated_data):
        # создаем рецепт
        # создаем теги
        # создаем ингредиенты
        pass

    def update(self, instance, validated_data):
        # обновляем ингредиенты
        # обновляем теги
        # обновляем рецепт
        pass

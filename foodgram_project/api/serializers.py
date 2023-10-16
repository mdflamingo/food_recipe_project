from rest_framework import serializers
import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'color', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class ReadCookingRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measure_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = CookingRecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
    image = Base64ImageField()

    class Meta:
        model = CookingRecipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time',
                  'image')

    def validate(self, data):
        tags = data.get('tags')
        ingredients = [element.get('id') for element in data.get('ingredients')]
        if not tags:
            raise serializers.ValidationError({'tags': 'Выберите тег!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги не должны повторяться'})
        if not ingredients:
            raise serializers.ValidationError({'ingredients': 'Невозможно создать рецепт без ингредиентов!'})
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError({'ingredients': 'Ингредиенты не должны повторяться!'})
        return data
    
        # tags = data.get('tags')
        # ingredients = data.get('ingredients')
        # if not tags or not ingredients:
        #     raise serializers.ValidationError({'tags': 'Выберите тег!'})
        # if len(tags) != len(set(tags)):
        #     raise serializers.ValidationError({'tags': 'Теги не должны повторяться'})
        # return data

    # добавить валидацию ингредиентов, игредиеты не должны повторятьсяю
    # реализовать уникальность ингредиентов на уровне класса
    # unique_together = ("name", "measurement_unit") в Meta

    def create(self, validated_data):
        # создаем рецепт
        # создаем теги
        # создаем ингредиенты
        recipe = CookingRecipe.objects.create(**validated_data)
        return recipe

    def update(self, instance, validated_data):
        # обновляем ингредиенты
        # обновляем теги
        # обновляем рецепт
        instance.tags = validated_data.get('tags', instance.tags)
        instance.ingredients = validated_data.get('ingredients', instance.ingredients)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

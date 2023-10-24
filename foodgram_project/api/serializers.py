from django.shortcuts import get_object_or_404
from rest_framework import serializers
import base64
import webcolors

from django.core.files.base import ContentFile

from recipes.models import (CookingRecipe,
                            Tag,
                            Ingredient,
                            CookingRecipeIngredient,
                            CookingRecipeTag)
from users.models import User, Follow


class ProfileSerializers(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return False


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
        fields = ('id', 'color', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class ReadCookingRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = CookingRecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    #print(f'!!!!!{id}')
    amount = serializers.IntegerField(min_value=1)
    print(amount)

    class Meta:
        model = CookingRecipeIngredient
        fields = ('id', 'amount')


class CookingRecipeListSerializer(serializers.ModelSerializer):
    # получение рецепта GET
    ingredients = ReadCookingRecipesSerializer(many=True)#source='recipe_ingredient')
    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializers(read_only=True)

    class Meta:
        model = CookingRecipe
        fields = ('ingredients', 'author',
                  'name', 'image', 'text', 'cooking_time', 'tags')


class CookingRecipesSerializer(serializers.ModelSerializer):
    # cоздание рецепта
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    #tags = TagSerializer(many=True)
    ingredients = AddIngredientsSerializer(many=True, source='ingredient_recipe')
    image = Base64ImageField()

    class Meta:
        model = CookingRecipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time',
                  'image')

    def validate(self, data):
        tags = data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        ingredients_id = [el.get('id') for el in ingredients]

        if not tags:
            raise serializers.ValidationError({'tags': 'Выберите тег!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги не должны повторяться'})
        if not ingredients:
            raise serializers.ValidationError({'ingredients': 'Невозможно создать рецепт без ингредиентов!'})
        if len(ingredients) != len(set(ingredients_id)):
            raise serializers.ValidationError({'ingredients': 'Ингредиенты не должны повторяться!'})
        # for id in ingredients_id:
        #     is_exist = Ingredient.objects.filter(id=id).exists()
        #     if not is_exist:
        #         raise serializers.ValidationError({'ingredients': 'Ингредиент c выбранным id не существует!'})
        print(f'111!!!!{data}!!!!2222')
        return data

    # добавить валидацию ингредиентов, игредиеты не должны повторятьсяю
    # реализовать уникальность ингредиентов на уровне класса
    # unique_together = ("name", "measurement_unit") в Meta

    # def create(self, validated_data):
    #     # создаем рецепт
    #     # создаем теги
    #     # создаем ингредиенты
    #     print(validated_data)
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     print(f'!!!!{ingredients}!!!!')
    #     print(type(ingredients))
    #     recipe = CookingRecipe.objects.create(**validated_data)
    #     for ingredient in ingredients:
    #         print(f'{ingredient}')
    #         amount = ingredient.get('amount')
    #         id = list(ingredient.keys())
    #         print(f'!!!{id}!!!')
    #         recipe_ingredient = get_object_or_404(Ingredient, id=id[0])
    #         CookingRecipeIngredient.objects.create(
    #             recipe=recipe,
    #             ingredient=recipe_ingredient,
    #             amount=amount)
            
    #     for tag in tags():
    #         recipe.add(tag)
    #     return recipe
    
    def create(self, validated_data):
        # создатьь рецепт, затем к созданному рецепту прикрутить теги и ингредиенты

        print(validated_data)
        tags = validated_data.pop('tags')
        recipe_ingredients = validated_data.pop('ingredients')
        recipe = CookingRecipe.objects.create(**validated_data)
        for tag in tags:
            CookingRecipeTag.objects.create(
                tag=tag,
                recipe=recipe
            )
        for ingredient in recipe_ingredients:
            ingr_id = ingredient.get('id')
            print(type(ingr_id))
            amount = ingredient.get('amount')
            print(type(amount))
            CookingRecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingr_id,
                amount=amount
            )
            print(222222222222)
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


class FollowListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CookingRecipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        pass

    def to_representation(self, instance):
        return FollowListSerializer(instance.following, context=self.context).data
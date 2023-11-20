from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from .constants import (AMOUNT_DEFAULT, COLOR_MAX_LEN,
                        MEASUREMENT_UNIT_MAX_LEN, NAME_MAX_LEN, SLUG_MAX_LEN)


class CookingRecipe(models.Model):
    """Модель кулинарного рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe')
    name = models.CharField(
        'Название',
        max_length=NAME_MAX_LEN)
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/')
    text = models.TextField(
        'Описание')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='CookingRecipeIngredient')
    tags = models.ManyToManyField(
        'Tag',)
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.name}: {self.text}'


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=NAME_MAX_LEN,
        unique=True)
    color = models.CharField(
        'Цвет',
        max_length=COLOR_MAX_LEN,
        unique=True)
    slug = models.SlugField(
        'Slug',
        max_length=SLUG_MAX_LEN,
        unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=NAME_MAX_LEN)

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MEASUREMENT_UNIT_MAX_LEN)

    class Meta:
        ordering = ('name', )
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class CookingRecipeIngredient(models.Model):
    """Промежуточная модель для кулинарного рецепта и ингредиента."""

    recipe = models.ForeignKey(
        CookingRecipe,
        on_delete=models.CASCADE,
        related_name='ingredient_used')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_used')
    amount = models.IntegerField(
        'Количество',
        default=AMOUNT_DEFAULT,
        validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite')
    recipe = models.ForeignKey(CookingRecipe,
                               on_delete=models.CASCADE,
                               related_name='recipe')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.recipe}'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(CookingRecipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_shopping_cart')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user}: {self.recipe}'

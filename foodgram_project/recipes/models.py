from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class CookingRecipe(models.Model):
    """Модель кулинарного рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe')
    name = models.CharField(
        'Название',
        max_length=200)
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/')
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
        max_length=200,
        unique=True)
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=200)

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200)

    class Meta:
        ordering = ('name', )
        # constraints = [
        #     models.UniqueConstraint(fields=['name',
        # 'measurement_unit'], name='name_measurement_unit')
        # ]
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
        default=1,
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

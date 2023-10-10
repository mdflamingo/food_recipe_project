from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class CookingRecipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        blank=True)
    name = models.CharField(
        'Название',
        max_length=200)
    # image = models.ImageField(
    #     'Фото рецепта',
    #     upload_to='static/recipe/')
    text = models.TextField(
        'Описание')
    ingredients = models.ManyToManyField(
        'Ingredients', 
        blank=False,
        through='CookingRecipeIngredients')
    tags = models.ManyToManyField(
        'Tag', related_name='recipes')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name


class Tag(models.Model):
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


class Ingredients(models.Model):
    name = models.CharField(
        'Название',
        max_length=200)

    measure_unit = models.CharField(
        'Единица измерения',
        max_length=200)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}, {self.measure_unit}'


class CookingRecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        CookingRecipe,
        on_delete=models.CASCADE,
        related_name='recipe')
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.IntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1)])

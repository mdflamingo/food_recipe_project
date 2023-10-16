from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class CookingRecipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        blank=False)
    name = models.CharField(
        'Название',
        max_length=200)
    # image = models.CharField(
    #     'Фото рецепта',
    #     max_length=200,
    #     blank=False)
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/',
        blank=False)
    text = models.TextField(
        'Описание')
    ingredients = models.ManyToManyField(
        'Ingredients',
        blank=False,
        through='CookingRecipeIngredients', related_name='recipe')
    tags = models.ManyToManyField(
        'Tag', related_name='recipe')
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

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200)

    class Meta:
        ordering = ('name', )
        # constraints = [
        #     models.UniqueConstraint(fields=['name', 'measurement_unit'], name='name_measurement_unit')
        # ]
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


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


class CookingRecipeTag(models.Model):
    recipe = models.ForeignKey(
        CookingRecipe,
        on_delete=models.CASCADE)
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE)

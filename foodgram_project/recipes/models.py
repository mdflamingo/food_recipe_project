from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CookingRecipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe')
    name = models.CharField(max_length=200)
    # image = models.CharField(max_length=200)
    text = models.TextField()
    ingredients = models.ManyToManyField('Ingredients',)
    tag = models.ManyToManyField('Tag',)
    cooking_time = models.IntegerField

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True, max_length=200)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=200)
    amount = models.IntegerField()
    measure_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name
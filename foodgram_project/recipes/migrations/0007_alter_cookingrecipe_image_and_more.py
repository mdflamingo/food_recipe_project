# Generated by Django 4.2.5 on 2023-11-08 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0006_alter_cookingrecipe_ingredients_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cookingrecipe",
            name="image",
            field=models.ImageField(upload_to="recipes/", verbose_name="Фото рецепта"),
        ),
        migrations.AlterField(
            model_name="cookingrecipe",
            name="ingredients",
            field=models.ManyToManyField(
                through="recipes.CookingRecipeIngredient", to="recipes.ingredient"
            ),
        ),
        migrations.AlterField(
            model_name="cookingrecipe",
            name="tags",
            field=models.ManyToManyField(to="recipes.tag"),
        ),
    ]

# Generated by Django 3.2.3 on 2023-11-20 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20231120_1145'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cookingrecipeingredient',
            name='unique_ingredient_amount',
        ),
    ]

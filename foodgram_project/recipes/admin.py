from django.contrib import admin

from recipes.models import (CookingRecipe, CookingRecipeIngredient, Favorite,
                            Ingredient, ShoppingList, Tag)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeIngredientsAdmin(admin.TabularInline):
    model = CookingRecipeIngredient
    extra = 1
    min_num = 1


@admin.register(CookingRecipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'cooking_time',
                    'get_ingredients',
                    'get_favorite_count')
    list_display_links = ('name',)
    inlines = (RecipeIngredientsAdmin,)
    list_filter = ('name', 'author', 'tags')

    def get_ingredients(self, obj):
        queryset = CookingRecipeIngredient.objects.filter(
            recipe_id=obj.id).all()

        return ', '.join(
            [f'{item.ingredient.name} {item.amount}'
             f'{item.ingredient.measurement_unit}'
             for item in queryset])

    def get_favorite_count(self, obj):
        return obj.recipe.count()


@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(BaseAdmin):
    list_display = ('user', 'recipe')

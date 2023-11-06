# from django.contrib import admin

# from recipes.models import (Ingredient, CookingRecipe,
#                             CookingRecipeIngredient, Tag,
#                             Favorite, ShoppingList)


# class BaseAdmin(admin.ModelAdmin):
#     empty_value_display = '-пусто-'


# class IngredientsAdmin(BaseAdmin):
#     pass


# class TagAdmin(admin.ModelAdmin):
#     pass


# class CookungRecipeIngredientsAdmin(admin.TabularInline):
#     model = CookingRecipeIngredient
#     extra = 1
#     min_num = 1


# class CookingRecipeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'cooking_time', 'get_ingredients')
#     list_display_links = ('name',)
#     # inlines = (RecipeIngredientsAdmin,)

#     def get_ingredients(self, obj):
#         queryset = CookingRecipeIngredient.objects.filter(recipe_id=obj.id).all()
#         return ', '.join([f' {item.ingredient.name} {item.amount} 'f'{item.ingredient.measurement_unit}' for item in queryset])


# admin.site.register(Ingredient, IngredientsAdmin)
# # admin.site.register(CookingRecipeIngredients, CookingRecipeIngredientsAdmin)
# admin.site.register(CookingRecipe, CookingRecipeAdmin)
# admin.site.register(Tag, TagAdmin)
# admin.site.register(ShoppingList)
# admin.site.register(Favorite)

from django.contrib import admin

from recipes.models import (
    Ingredient,
    CookingRecipe,
    CookingRecipeIngredient,
    Tag
)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    pass


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    pass


class RecipeIngredientsAdmin(admin.TabularInline):
    model = CookingRecipeIngredient
    extra = 1
    min_num = 1


@admin.register(CookingRecipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'cooking_time',
                    'get_ingredients')
    list_display_links = ('name',)
    inlines = (RecipeIngredientsAdmin,)

    def get_ingredients(self, obj):
        queryset = CookingRecipeIngredient.objects.filter(
            recipe_id=obj.id).all()

        return ', '.join(
            [f'{item.ingredient.name} {item.amount}'
             f'{item.ingredient.measurement_unit}'
             for item in queryset])

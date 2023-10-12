from django.contrib import admin

from recipes.models import (Ingredients, CookingRecipe, CookingRecipeIngredients, Tag)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class IngredientsAdmin(BaseAdmin):
    pass

class TagAdmin(admin.ModelAdmin):
    pass

class CookungRecipeIngredientsAdmin(admin.TabularInline):
    model = CookingRecipeIngredients
    extra = 1
    min_num = 1


class CookingRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time', 'get_ingredients')
    list_display_links = ('name',)
    # inlines = (RecipeIngredientsAdmin,)

    def get_ingredients(self, obj):
        queryset = CookingRecipeIngredients.objects.filter(recipe_id=obj.id).all()
        return ', '.join([f' {item.ingredient.name} {item.amount} 'f'{item.ingredient.measurement_unit}' for item in queryset])


admin.site.register(Ingredients, IngredientsAdmin)
# admin.site.register(CookingRecipeIngredients, CookingRecipeIngredientsAdmin)
admin.site.register(CookingRecipe, CookingRecipeAdmin)
admin.site.register(Tag, TagAdmin)
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, FilterSet,
                                           NumberFilter)

from recipes.models import CookingRecipe


class RecipeFilter(FilterSet):
    """Класс для фильтрации рецептов по полям is_favorited,
    is_in_shopping_cart, tags, author."""

    is_favorited = BooleanFilter(method='filter_is_favorited',
                                 field_name='is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart',
                                        field_name='is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug',)
    author = NumberFilter(field_name='author')

    class Meta:
        model = CookingRecipe
        fields = ('is_favorited',
                  'is_in_shopping_cart',
                  'author',
                  'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return CookingRecipe.objects.filter(
                recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return CookingRecipe.objects.filter(
                recipe_shopping_cart__user=user)

        return queryset

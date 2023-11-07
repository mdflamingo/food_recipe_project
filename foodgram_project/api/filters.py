
from django_filters.rest_framework import (FilterSet,
                                           AllValuesMultipleFilter,
                                           BooleanFilter,
                                           NumberFilter)

from recipes.models import CookingRecipe


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method='filter_is_favorited',
                                 field_name='is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart',
                                        field_name='is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags_slug',
                                   to_field_name='slug')
    author = NumberFilter(field_name='author')

    class Meta:
        model = CookingRecipe
        fields = ('is_favorited',
                  'is_in_shopping_cart',
                  'author',
                  'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_shopping_cart=self.request.user)

        return queryset

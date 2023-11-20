from django.urls import include, path, re_path
from rest_framework import routers

from .views import (APIFavorite, APIFollow, APIShoppingList,
                    CookingRecipeViewSet, FoodgramUserViewSet,
                    IngredientsViewSet, TagViewSet)

router = routers.DefaultRouter()

router.register(r'recipes', CookingRecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', FoodgramUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),

    path('recipes/<int:pk>/favorite/', APIFavorite.as_view(),
         name='recipes_favorite'),
    path('users/<int:pk>/subscribe/', APIFollow.as_view(),
         name='user_follow'),
    path('recipes/<int:pk>/shopping_cart/', APIShoppingList.as_view(),
         name='recipes_shopping_cart')
]

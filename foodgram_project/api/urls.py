from rest_framework import routers
from django.urls import include, path, re_path
# from djoser.views import UserViewSet
from .views import (CookingRecipeViewSet,
                    IngredientsViewSet,
                    TagViewSet,
                    UserViewSet,
                    APIFollow,
                    APIFavorite,
                    APIShoppingList)

router = routers.DefaultRouter()

router.register(r'recipes', CookingRecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),

    path('recipes/<int:pk>/favorite/', APIFavorite.as_view()),
    path('users/<int:pk>/subscribe/', APIFollow.as_view()),
    path('recipes/<int:pk>/shopping_cart/', APIShoppingList.as_view())
]

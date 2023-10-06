from rest_framework import routers
from django.urls import include, path, re_path
from .views import CookingRecipeViewSet, IngredientsViewSet, TagViewSet, CustomUserViewSet

router = routers.DefaultRouter()

router.register(r'recipes', CookingRecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),

]

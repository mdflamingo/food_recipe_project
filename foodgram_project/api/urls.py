from rest_framework import routers
from django.urls import include, path

from .views import CookingRecipeViewSet, IngredientsViewSet, TagViewSet, UserViewset

router = routers.DefaultRouter()

router.register(r'recipes', CookingRecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', UserViewset)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt'))


]

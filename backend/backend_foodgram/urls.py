from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeCreateViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeCreateViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls))
]
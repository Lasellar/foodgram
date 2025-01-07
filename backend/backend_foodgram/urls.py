from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    UserSubscriptionView, UserSubscriptionsViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', UserSubscriptionView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

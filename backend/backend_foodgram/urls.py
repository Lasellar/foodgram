from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    UserSubscriptionView, UserSubscriptionsViewSet,
    LoginView, LogOutView, UserViewSet, AvatarView,
    UserPasswordReset
)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(
    r'users/subscriptions', UserSubscriptionsViewSet,
    basename='users-subscriptions'
)
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-login'),
    path('auth/token/logout/', LogOutView.as_view(), name='token-logout'),
    path('users/<int:user_id>/subscribe/', UserSubscriptionView.as_view()),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path('', include(router.urls))
]

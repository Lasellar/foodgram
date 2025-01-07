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
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-obtain'),
    path('auth/token/logout/', LogOutView.as_view(), name='token-obtain'),
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', UserSubscriptionView.as_view()),
    path('users/me/avatar', AvatarView.as_view(), name='avatar'),
    path(
        'users/me/set_password/', UserPasswordReset.as_view(),
        name='reset-password'
    ),
    # path('', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

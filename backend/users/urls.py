from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SignUpView, LoginView, LogOutView, UserViewSet, AvatarView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-get'),  # получение токена
    path('auth/token/logout/', LogOutView.as_view(), name='token-del'),  # удаление токена
    path('users/', SignUpView.as_view(), name='signup'),  # регистрация пользователя
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),  # замена и удаление аватара
    path('', include(router.urls))
]

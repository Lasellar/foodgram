from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignUpView, TokenView, UserViewSet, UserMeView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/', SignUpView.as_view(), name='signup'),  # регистрация
    path('users/', ..., name='users-all'),  # список пользователей
    path('users/me/avatar/', ..., name='user-avatar'),  # добавление/удаление аватара
    path('users/set_password/', ..., name='user-reset-password'),  # изменение пароля
    path('auth/token/login/', TokenView.as_view(), name='token-get'),  # получение токена
    path('auth/token/login/', TokenView.as_view(), name='token-del'),  # удаление токена
    path('users/me/', UserMeView.as_view(), name='user-me'),  # текущий пользователь
    path('users/...', ..., name='user-get'),  # профиль пользователя
    path('', include(router.urls))
]

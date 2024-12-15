from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import SignUpView, TokenView, UserViewSet, UserMeView

router = DefaultRouter()
router.register(r'users', ..., basename='user')

"""urlpatterns = [
    path('users/', ..., name='signup'),  # регистрация
    path('users/', ..., name='users-all'),  # список пользователей
    path('users/me/avatar/', ..., name='user-avatar'),  # добавление/удаление аватара
    path('users/set_password/', ..., name='user-reset-password'),  # изменение пароля
    path('auth/token/login/', ..., name='token-get'),  # получение токена
    path('auth/token/login/', ..., name='token-del'),  # удаление токена
    path('users/me/', ..., name='user-me'),  # текущий пользователь
    path('users/...', ..., name='user-get'),  # профиль пользователя
    path('', include(router.urls))
]"""

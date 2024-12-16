from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignUpView, LoginView, LogOutView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-get'),  # получение токена
    path('auth/token/logout/', LogOutView.as_view(), name='token-del'),  # удаление токена
    path('users/', SignUpView.as_view(), name='signup'),  # регистрация пользователя
    path('', include(router.urls))
]

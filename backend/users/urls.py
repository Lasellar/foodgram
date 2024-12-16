from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignUpView, LoginView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-get'),  # получение токена
    path('users/', SignUpView.as_view(), name='signup'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]

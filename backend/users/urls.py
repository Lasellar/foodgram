from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, LoginView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/token/login/', LoginView.as_view(), name='token-obtain'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

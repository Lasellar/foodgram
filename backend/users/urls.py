from django.urls import path, include

from .views import (
    UserSubscriptionView, UserSubscriptionsViewSet
)

urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', UserSubscriptionView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

from django.contrib import admin
from django.urls import path, include

from backend_foodgram.views import redirect_short_link_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend_foodgram.urls')),
    path('s/<slug:short_link>/', redirect_short_link_view)
]

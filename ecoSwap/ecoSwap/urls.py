from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('exchanges/', include('exchanges.urls')),
    path('rating/', include('reputation.urls')),
    path('publications/', include('publications.urls')),
]

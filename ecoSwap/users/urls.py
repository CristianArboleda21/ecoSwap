from django.urls import path
from users.views import views

urlpatterns = [
    path('public/', views.public_view, name='public_view'),
]
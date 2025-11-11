from django.urls import path
from reputation.views import views

urlpatterns = [
    path('rate-exchange', views.rate_exchange, name='rate_exchange'),
    path('get-reputation', views.get_reputation, name='get_reputation'),
]
from django.urls import path
from exchanges.views import views

urlpatterns = [
    path('send-exchange', views.create_exchange, name='create_exchange'),
    path('respond-exchange', views.respond_exchange, name='respond_exchange'),
    path('cancel-exchange', views.cancel_exchange, name='cancel_exchange'),
    path('list-exchanges', views.list_exchanges, name='list_exchanges'),
]
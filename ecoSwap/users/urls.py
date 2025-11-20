from django.urls import path
from users.views import views

urlpatterns = [
    path('register-user', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('profile', views.get_user_profile, name='profile'),
    path('update-profile', views.edit_user_profile, name='update_profile'),
    path('send-code', views.send_code_password_reset, name='send_code_password_reset'),
    path('reset-password', views.reset_password_code, name='reset_password_code'),
    path('get-user-publication', views.get_user_profile_by_email, name='get_user_by_email'),
]
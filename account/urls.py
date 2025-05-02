from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'account'
urlpatterns = [
    path('', index, name='index'),
   # path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    
]
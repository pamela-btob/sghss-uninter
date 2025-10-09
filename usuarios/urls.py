from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.user_registration, name='user-registration'),
    path('perfil/', views.user_profile, name='user-profile'),
]
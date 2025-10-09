from django.urls import path
from usuarios import views

urlpatterns = [
    path('api/agendamentos/', views.agendamento_list_create, name='agendamento-list-create'),
    path('api/agendamentos/<int:pk>/', views.agendamento_detail, name='agendamento-detail'),
]
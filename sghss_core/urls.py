from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importações diretas das views
from usuarios.views import (
    user_registration, 
    user_profile, 
    agendamento_list_create, 
    agendamento_detail,
    prontuario_list_create,  # <-- NOVA IMPORTACAO
    prontuario_detail        # <-- NOVA IMPORTACAO
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs do JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # URLs dos usuários
    path('api/usuarios/registro/', user_registration, name='user-registration'),
    path('api/usuarios/perfil/', user_profile, name='user-profile'),
    
    # URLs dos agendamentos
    path('api/agendamentos/', agendamento_list_create, name='agendamento-list-create'),
    path('api/agendamentos/<int:pk>/', agendamento_detail, name='agendamento-detail'),
    
    # NOVAS URLs dos prontuários
    path('api/prontuarios/', prontuario_list_create, name='prontuario-list-create'),
    path('api/prontuarios/<int:pk>/', prontuario_detail, name='prontuario-detail'),
]
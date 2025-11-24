from django.contrib import admin
import os
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
from usuarios.views import (
    user_registration, 
    user_profile, 
    agendamento_list_create, 
    agendamento_detail,
    prontuario_list_create,
    prontuario_detail,
    exame_list_create,      
    exame_detail,           
    dashboard_estatisticas,    
    relatorio_agendamentos,    
    relatorio_financeiro,
    cancelar_agendamento,
    historico_paciente,)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/usuarios/registro/', user_registration, name='user-registration'),
    path('api/usuarios/perfil/', user_profile, name='user-profile'),
    path('api/agendamentos/', agendamento_list_create, name='agendamento-list-create'),
    path('api/agendamentos/<int:pk>/', agendamento_detail, name='agendamento-detail'),
    path('api/prontuarios/', prontuario_list_create, name='prontuario-list-create'),
    path('api/prontuarios/<int:pk>/', prontuario_detail, name='prontuario-detail'),
    path('api/exames/', exame_list_create, name='exame-list-create'),
    path('api/exames/<int:pk>/', exame_detail, name='exame-detail'),
    path('api/admin/dashboard/', dashboard_estatisticas, name='dashboard-estatisticas'),
    path('api/admin/relatorios/agendamentos/', relatorio_agendamentos, name='relatorio-agendamentos'),
    path('api/admin/relatorios/financeiro/', relatorio_financeiro, name='relatorio-financeiro'),
    path('api/agendamentos/<int:pk>/cancelar/', cancelar_agendamento, name='cancelar-agendamento'),
    path('api/pacientes/<int:paciente_id>/historico/', historico_paciente, name='historico-paciente'),
    path('api/pacientes/historico/', historico_paciente, name='meu-historico'), 
    path('', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))

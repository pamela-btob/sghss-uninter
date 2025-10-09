from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import CustomUser, Agendamento, Prontuario, Exame
from .serializers import UserRegistrationSerializer, AgendamentoSerializer, ProntuarioSerializer, ExameSerializer

def frontend(request):
    return render(request, 'index.html')

# 1. Registro de usuário
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Usuário criado com sucesso!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Perfil do usuário
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'tipo_usuario': user.tipo_usuario,
        'message': 'Você está autenticado!'
    })

# 3. Listar e criar agendamentos
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def agendamento_list_create(request):
    if request.method == 'GET':
        if request.user.tipo_usuario == 'P':
            agendamentos = Agendamento.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == 'M':
            agendamentos = Agendamento.objects.filter(medico=request.user)
        else:
            agendamentos = Agendamento.objects.all()
        
        serializer = AgendamentoSerializer(agendamentos, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AgendamentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Detalhe do agendamento
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def agendamento_detail(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if (request.user != agendamento.paciente and 
        request.user != agendamento.medico and 
        request.user.tipo_usuario != 'A'):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = AgendamentoSerializer(agendamento)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AgendamentoSerializer(agendamento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        agendamento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def prontuario_list_create(request):
    """
    Listar ou criar prontuários
    - Pacientes veem apenas seus prontuários
    - Médicos veem prontuários de seus pacientes
    - Administradores veem todos
    """
    if request.method == 'GET':
        if request.user.tipo_usuario == 'P':
            prontuarios = Prontuario.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == 'M':
            prontuarios = Prontuario.objects.filter(medico=request.user)
        else:  # Administrador
            prontuarios = Prontuario.objects.all()
        
        serializer = ProntuarioSerializer(prontuarios, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
    # Apenas médicos podem criar prontuários
        if request.user.tipo_usuario != 'M':
            return Response(
            {"error": "Apenas médicos podem criar prontuários."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Adiciona o médico automaticamente aos dados
    data = request.data.copy()
    data['medico'] = request.user.id
    
    serializer = ProntuarioSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def prontuario_detail(request, pk):
    """
    Detalhar ou atualizar prontuário específico
    """
    try:
        prontuario = Prontuario.objects.get(pk=pk)
    except Prontuario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Verifica permissão: paciente, médico responsável ou admin
    if (request.user != prontuario.paciente and 
        request.user != prontuario.medico and 
        request.user.tipo_usuario != 'A'):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ProntuarioSerializer(prontuario)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Apenas o médico responsável pode editar
        if request.user != prontuario.medico:
            return Response(
                {"error": "Apenas o médico responsável pode editar o prontuário."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProntuarioSerializer(prontuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exame_list_create(request):
    """
    Listar ou criar exames
    - Pacientes veem apenas seus exames
    - Médicos veem exames de seus pacientes
    - Administradores veem todos
    """
    if request.method == 'GET':
        if request.user.tipo_usuario == 'P':
            exames = Exame.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == 'M':
            exames = Exame.objects.filter(medico=request.user)
        else:  # Administrador
            exames = Exame.objects.all()
        
        serializer = ExameSerializer(exames, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Apenas médicos podem solicitar exames
        if request.user.tipo_usuario != 'M':
            return Response(
                {"error": "Apenas médicos podem solicitar exames."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Adiciona o médico automaticamente aos dados
        data = request.data.copy()
        data['medico'] = request.user.id
        
        serializer = ExameSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def exame_detail(request, pk):
    """
    Detalhar ou atualizar exame específico
    """
    try:
        exame = Exame.objects.get(pk=pk)
    except Exame.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Verifica permissão: paciente, médico responsável ou admin
    if (request.user != exame.paciente and 
        request.user != exame.medico and 
        request.user.tipo_usuario != 'A'):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ExameSerializer(exame)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Paciente só pode ver, médico pode editar, admin pode tudo
        if request.user.tipo_usuario == 'P':
            return Response(
                {"error": "Pacientes não podem editar exames."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = request.method == 'PATCH'
        serializer = ExameSerializer(exame, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_estatisticas(request):
    """
    Dashboard administrativo com estatísticas do sistema
    Apenas administradores podem acessar
    """
    if request.user.tipo_usuario != 'A':
        return Response(
            {"error": "Apenas administradores podem acessar o dashboard."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Estatísticas de usuários
    total_usuarios = CustomUser.objects.count()
    total_pacientes = CustomUser.objects.filter(tipo_usuario='P').count()
    total_medicos = CustomUser.objects.filter(tipo_usuario='M').count()
    total_administradores = CustomUser.objects.filter(tipo_usuario='A').count()
    
    # Estatísticas de agendamentos
    total_agendamentos = Agendamento.objects.count()
    agendamentos_hoje = Agendamento.objects.filter(
        data_agendamento__date=timezone.now().date()
    ).count()
    agendamentos_mes = Agendamento.objects.filter(
        data_agendamento__month=timezone.now().month,
        data_agendamento__year=timezone.now().year
    ).count()
    
    # Estatísticas por status de agendamento
    agendamentos_agendados = Agendamento.objects.filter(status='agendado').count()
    agendamentos_confirmados = Agendamento.objects.filter(status='confirmado').count()
    agendamentos_realizados = Agendamento.objects.filter(status='realizado').count()
    agendamentos_cancelados = Agendamento.objects.filter(status='cancelado').count()
    
    # Estatísticas de prontuários
    total_prontuarios = Prontuario.objects.count()
    prontuarios_mes = Prontuario.objects.filter(
        criado_em__month=timezone.now().month,
        criado_em__year=timezone.now().year
    ).count()
    
    # Estatísticas de exames
    total_exames = Exame.objects.count()
    exames_solicitados = Exame.objects.filter(status='solicitado').count()
    exames_finalizados = Exame.objects.filter(status='finalizado').count()
    
    # Tipos de consulta mais comuns
    consultas_presencial = Agendamento.objects.filter(tipo_consulta='presencial').count()
    consultas_telemedicina = Agendamento.objects.filter(tipo_consulta='telemedicina').count()
    
    # Exames mais solicitados
    from django.db.models import Count
    exames_mais_solicitados = Exame.objects.values('tipo_exame').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    dados = {
        # Usuários
        "usuarios": {
            "total": total_usuarios,
            "pacientes": total_pacientes,
            "medicos": total_medicos,
            "administradores": total_administradores
        },
        
        # Agendamentos
        "agendamentos": {
            "total": total_agendamentos,
            "hoje": agendamentos_hoje,
            "este_mes": agendamentos_mes,
            "por_status": {
                "agendados": agendamentos_agendados,
                "confirmados": agendamentos_confirmados,
                "realizados": agendamentos_realizados,
                "cancelados": agendamentos_cancelados
            },
            "por_tipo": {
                "presencial": consultas_presencial,
                "telemedicina": consultas_telemedicina
            }
        },
        
        # Prontuários
        "prontuarios": {
            "total": total_prontuarios,
            "este_mes": prontuarios_mes
        },
        
        # Exames
        "exames": {
            "total": total_exames,
            "solicitados": exames_solicitados,
            "finalizados": exames_finalizados,
            "mais_solicitados": list(exames_mais_solicitados)
        },
        
        # Metadados
        "metadados": {
            "data_geracao": timezone.now(),
            "periodo": "todo o período"
        }
    }
    
    return Response(dados)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_agendamentos(request):
    """
    Relatório detalhado de agendamentos
    Filtros por período, médico, status
    """
    if request.user.tipo_usuario != 'A':
        return Response(
            {"error": "Apenas administradores podem acessar relatórios."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filtros opcionais
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    medico_id = request.GET.get('medico_id')
    status_agendamento = request.GET.get('status')
    
    agendamentos = Agendamento.objects.all()
    
    # Aplicar filtros
    if data_inicio:
        agendamentos = agendamentos.filter(data_agendamento__date__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data_agendamento__date__lte=data_fim)
    if medico_id:
        agendamentos = agendamentos.filter(medico_id=medico_id)
    if status_agendamento:
        agendamentos = agendamentos.filter(status=status_agendamento)
    
    # Serializar dados
    serializer = AgendamentoSerializer(agendamentos, many=True)
    
    # Estatísticas do relatório filtrado
    total = agendamentos.count()
    por_status = agendamentos.values('status').annotate(total=Count('id'))
    por_tipo = agendamentos.values('tipo_consulta').annotate(total=Count('id'))
    
    relatorio = {
        "dados": serializer.data,
        "estatisticas": {
            "total": total,
            "por_status": list(por_status),
            "por_tipo_consulta": list(por_tipo)
        },
        "filtros_aplicados": {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "medico_id": medico_id,
            "status": status_agendamento
        }
    }
    
    return Response(relatorio)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_financeiro(request):
    """
    Relatório financeiro simulado (para demonstração)
    Em um sistema real, integraria com módulo financeiro
    """
    if request.user.tipo_usuario != 'A':
        return Response(
            {"error": "Apenas administradores podem acessar relatórios financeiros."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Dados simulados para demonstração
    # Em um sistema real, isso viria de um módulo financeiro
    receita_mensal = {
        "consultas_presencial": 150 * 120.00,  # 150 consultas a R$ 120,00
        "consultas_telemedicina": 80 * 80.00,   # 80 consultas a R$ 80,00
        "exames": 45 * 50.00,                   # 45 exames a R$ 50,00
        "total": (150 * 120.00) + (80 * 80.00) + (45 * 50.00)
    }
    
    despesas_mensais = {
        "folha_pagamento": 25000.00,
        "manutencao_equipamentos": 5000.00,
        "suprimentos": 3000.00,
        "total": 25000.00 + 5000.00 + 3000.00
    }
    
    lucro_mensal = receita_mensal["total"] - despesas_mensais["total"]
    
    relatorio_financeiro = {
        "receitas": receita_mensal,
        "despesas": despesas_mensais,
        "lucro_liquido": lucro_mensal,
        "margem_lucro": (lucro_mensal / receita_mensal["total"]) * 100 if receita_mensal["total"] > 0 else 0,
        "periodo": f"{timezone.now().strftime('%B %Y')} (dados simulados)",
        "observacao": "Este é um relatório demonstrativo com dados simulados para fins de demonstração do sistema."
    }
    
    return Response(relatorio_financeiro)
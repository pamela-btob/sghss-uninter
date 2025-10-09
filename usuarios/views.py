from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import CustomUser, Agendamento, Prontuario
from .serializers import ProntuarioSerializer, UserRegistrationSerializer, AgendamentoSerializer

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
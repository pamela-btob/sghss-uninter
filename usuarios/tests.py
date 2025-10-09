from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser, Agendamento, Prontuario

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.paciente_data = {
            'username': 'testepaciente',
            'email': 'paciente@test.com',
            'password': 'Senha123@',
            'password2': 'Senha123@',
            'tipo_usuario': 'P',
            'cpf': '111.222.333-44'
        }
        
        self.medico_data = {
            'username': 'drteste',
            'email': 'medico@test.com', 
            'password': 'Senha123@',
            'password2': 'Senha123@',
            'tipo_usuario': 'M',
            'crm': 'CRM-TEST123'
        }

    def test_user_registration(self):
        """Teste de registro de usuário"""
        url = reverse('user-registration')
        response = self.client.post(url, self.paciente_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_user_login(self):
        """Teste de login com JWT"""
        # Primeiro cria o usuário
        self.client.post(reverse('user-registration'), self.paciente_data, format='json')
        
        # Faz login
        login_data = {
            'username': 'testepaciente',
            'password': 'Senha123@'
        }
        url = reverse('token_obtain_pair')
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class AgendamentoTests(APITestCase):
    def setUp(self):
        # Cria usuários de teste
        self.paciente = CustomUser.objects.create_user(
            username='pacientetest', password='senha123', tipo_usuario='P'
        )
        self.medico = CustomUser.objects.create_user(
            username='medicotest', password='senha123', tipo_usuario='M'  
        )

    def test_create_agendamento(self):
        """Teste de criação de agendamento"""
        self.client.force_authenticate(user=self.paciente)
        
        agendamento_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'data_agendamento': '2025-10-10T10:00:00Z',
            'tipo_consulta': 'presencial'
        }
        
        url = reverse('agendamento-list-create')
        response = self.client.post(url, agendamento_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
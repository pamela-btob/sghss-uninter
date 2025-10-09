from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import CustomUser, Agendamento, Prontuario
from django.utils import timezone

class SecurityTests(APITestCase):
    def setUp(self):
        self.paciente = CustomUser.objects.create_user(
            username='paciente_seg', 
            password='Senha123@', 
            tipo_usuario='P',
            cpf='123.456.789-00'
        )
        self.medico = CustomUser.objects.create_user(
            username='medico_seg', 
            password='Senha123@', 
            tipo_usuario='M',
            crm='CRM-SEC123'
        )

    def test_data_encryption(self):
        """Testa se dados sensíveis estão criptografados no banco"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT cpf FROM usuarios_customuser WHERE username = 'paciente_seg'")
            row = cursor.fetchone()
            cpf_criptografado = row[0]
            
        # Verifica se está criptografado (não é o CPF original)
        self.assertNotEqual(cpf_criptografado, '123.456.789-00')
        self.assertTrue(len(cpf_criptografado) > 20)

    def test_access_control_patient(self):
        """Testa que paciente não pode acessar dados de outros pacientes"""
        self.client.force_authenticate(user=self.paciente)
        
        # Tenta acessar lista de usuários (deveria ser negado)
        response = self.client.get('/api/usuarios/')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_invalid_token_rejected(self):
        """Testa que token inválido é rejeitado"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token_invalido_123')
        response = self.client.get('/api/usuarios/perfil/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_token_rejected(self):
        """Testa que requisição sem token é rejeitada"""
        self.client.credentials()
        response = self.client.get('/api/usuarios/perfil/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class BusinessLogicTests(APITestCase):
    def setUp(self):
        self.paciente = CustomUser.objects.create_user(
            username='paciente_bl', password='senha123', tipo_usuario='P'
        )
        self.medico = CustomUser.objects.create_user(
            username='medico_bl', password='senha123', tipo_usuario='M'
        )

    def test_appointment_past_date_validation(self):
        """Testa que não pode criar agendamento no passado"""
        self.client.force_authenticate(user=self.paciente)
        
        agendamento_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'data_agendamento': '2020-01-01T10:00:00Z',
            'tipo_consulta': 'presencial'
        }
        
        response = self.client.post('/api/agendamentos/', agendamento_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patient_cannot_create_medical_record(self):
        """Testa que paciente não pode criar prontuário"""
        self.client.force_authenticate(user=self.paciente)
        
        prontuario_data = {
            'paciente': self.paciente.id,
            'medico': self.medico.id,
            'titulo': 'Tentativa de paciente',
            'descricao': 'Paciente tentando criar prontuário'
        }
        
        response = self.client.post('/api/prontuarios/', prontuario_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class BasicTests(APITestCase):
    def test_user_registration(self):
        """Teste básico de registro de usuário"""
        user_data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'Senha123@',
            'password2': 'Senha123@',
            'tipo_usuario': 'P',
            'cpf': '111.222.333-44'
        }
        
        url = reverse('user-registration')
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Teste básico de login"""
        # Primeiro cria o usuário
        user = CustomUser.objects.create_user(
            username='loginuser', 
            password='Senha123@', 
            tipo_usuario='P'
        )
        
        # Faz login
        login_data = {
            'username': 'loginuser',
            'password': 'Senha123@'
        }
        url = reverse('token_obtain_pair')
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
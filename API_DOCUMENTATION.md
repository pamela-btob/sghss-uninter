
# Sistema de Autenticação
# Registrar Usuário
POST /api/usuarios/registro/

Body:
{
  "username": "maria.silva",
  "email": "maria@email.com",
  "password": "senha123",
  "nome": "Maria Silva"
}

Resposta (201 Created):
{
  "id": 1,
  "username": "maria.silva",
  "email": "maria@email.com",
  "nome": "Maria Silva"
}

# Login - Obter Token
POST /api/token/

Body:
{
  "username": "maria.silva",
  "password": "senha123"
}

Resposta (200 OK):
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Refresh Token:
POST /api/token/refresh/

Body:
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Gestão de Usuários
# Perfil do Usuário
GET /api/usuarios/perfil/
Headers: Authorization: Bearer <token>

Resposta (200 OK):
{
  "id": 1,
  "username": "maria.silva",
  "email": "maria@email.com",
  "nome": "Maria Silva",
  "data_cadastro": "2024-01-15T10:30:00Z"
}

# Gestão de Pacientes
# Listar Pacientes
GET /api/pacientes/
Headers: Authorization: Bearer <token>

Resposta (200 OK):
[
  {
    "id": 1,
    "nome": "João Santos",
    "email": "joao@email.com",
    "telefone": "11999999999",
    "data_nascimento": "1985-05-15",
    "endereco": "Rua das Flores, 123",
    "alergias": "Penicilina",
    "data_cadastro": "2024-01-15T10:30:00Z"
  }
]

# Criar Paciente
POST /api/pacientes/
Headers: Authorization: Bearer <token>

Body:
{
  "nome": "João Santos",
  "cpf": "12345678901",
  "telefone": "11999999999",
  "email": "joao@email.com",
  "data_nascimento": "1985-05-15",
  "endereco": "Rua das Flores, 123",
  "alergias": "Penicilina",
  "medicamentos_uso": "Omeprazol",
  "historico_doencas": "Hipertensão"
}

Resposta (201 Created):
{
  "id": 1,
  "nome": "João Santos",
  "email": "joao@email.com",
  "telefone": "11999999999",
  "data_nascimento": "1985-05-15",
  "endereco": "Rua das Flores, 123",
  "alergias": "Penicilina",
  "medicamentos_uso": "Omeprazol",
  "historico_doencas": "Hipertensão",
  "data_cadastro": "2024-01-15T10:30:00Z"
}

# Detalhes do Paciente
GET /api/pacientes/{id}/
Headers: Authorization: Bearer <token>

# Gestão de Profissionais de Saúde
# Listar Profissionais
GET /api/profissionais/
Headers: Authorization: Bearer <token>

Resposta (200 OK):
[
  {
    "id": 1,
    "nome": "Dr. Carlos Mendes",
    "email": "carlos@email.com",
    "telefone": "11888888888",
    "especialidade": "cardiologia",
    "crm": "CRM/SP-123456",
    "endereco_consultorio": "Av. Paulista, 1000",
    "data_cadastro": "2024-01-15T10:30:00Z"
  }
]

# Criar Profissional
POST /api/profissionais/
Headers: Authorization: Bearer <token>

Body:
{
  "nome": "Dr. Carlos Mendes",
  "cpf": "98765432100",
  "telefone": "11888888888",
  "email": "carlos@email.com",
  "crm": "CRM/SP-123456",
  "especialidade": "cardiologia",
  "endereco_consultorio": "Av. Paulista, 1000"
}

# Gestão de Agendamentos
# Listar Agendamentos

GET /api/agendamentos/
Headers: Authorization: Bearer <token>

# Criar Agendamento
POST /api/agendamentos/
Headers: Authorization: Bearer <token>

Body:
{
  "paciente": 1,
  "profissional": 1,
  "data_agendamento": "2024-12-15T14:30:00",
  "tipo_consulta": "presencial",
  "descricao": "Consulta de rotina",
  "status": "agendado"
}

# Cancelar Agendamento
POST /api/agendamentos/{id}/cancelar/
Headers: Authorization: Bearer <token>

# Prontuários Eletrônicos
# Listar Prontuários
GET /api/prontuarios/
Headers: Authorization: Bearer <token>

# Criar Prontuário
POST /api/prontuarios/
Headers: Authorization: Bearer <token>

Body:
{
  "paciente": 1,
  "profissional": 1,
  "agendamento": 1,
  "sintomas": "Dor de cabeça e febre",
  "diagnostico": "Sinusite",
  "prescricao_medicamentos": "Dipirona 500mg 6/6h",
  "observacoes": "Paciente orientado a retornar se persistirem os sintomas"
}

# Gestão de Exames
# Listar Exames
GET /api/exames/
Headers: Authorization: Bearer <token>

# Criar Exame
POST /api/exames/
Headers: Authorization: Bearer <token>

Body:
{
  "paciente": 1,
  "profissional": 1,
  "tipo_exame": "hemograma",
  "descricao": "Hemograma completo",
  "resultado": "Resultados dentro da normalidade",
  "data_realizacao": "2024-12-10",
  "status": "concluido"
}

# Dashboard Administrativo
# Estatísticas do Sistema
GET /api/admin/dashboard/
Headers: Authorization: Bearer <token>

Resposta (200 OK):
{
  "total_pacientes": 150,
  "total_profissionais": 25,
  "consultas_hoje": 12,
  "taxa_ocupacao": 78.5,
  "receita_mensal": 125000.00
}

# Relatório de Agendamentos
GET /api/admin/relatorios/agendamentos/
Headers: Authorization: Bearer <token>
Parâmetros Query:
data_inicio (opcional): "2024-01-01"
data_fim (opcional): "2024-01-31"



Desenvolvido por
Pamela - UNINTER - Projeto Multidisciplinar 2025

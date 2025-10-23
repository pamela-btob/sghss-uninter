<h1 align="center"> SGHSS - Sistema de Gestão Hospitalar e de Serviços de Saúde </h1>

# Sobre o Projeto:
Sistema completo de gestão hospitalar desenvolvido em Django REST Framework com foco em Back-end, incluindo autenticação JWT, criptografia de dados sensíveis (LGPD) e controle de acesso por perfis de usuário.


# Tecnologias Utilizadas
- Back-end: Django 5.2.6 + Django REST Framework 3.15.1, JWT (Simple JWT), SQLite (Desenvolvimento) / MySQL (Produção), Criptografia Fernet para dados sensíveis, django-cors-headers para integração front-end
- Front-end: HTML5, CSS3, JavaScript. Templates Django para interface administrativa

# Segurança e LGPD e Implementações de Segurança: 
Autenticação JWT com tokens de acesso e refresh, Criptografia Fernet para dados sensíveis (CPF, telefone, CRM), Controle de acesso baseado em tokens, Validação de dados de entrada, Logs de auditoria automáticos

# Dados Criptografados: 
CPF de pacientes e profissionais, Telefones, CRM e registros profissionais, E-mails, Dados de saúde sensíveis

# Como Executar o Projeto:
Pré-requisitos: 
- Python 3.8+
- Django 5.2.6
- Django REST Framework

# Instalação:
Clone o repositório: git clone https://github.com/pamela-btob/sghss-uninter.git, execute: cd sghss-uninter

# Instale as dependências:
pip install -r requirements.txt

# Execute as migrações: 
python manage.py makemigrations e python manage.py migrate

# Execute o servidor: 
python manage.py runserver

# Variáveis de Ambiente: 
settings.py, FIELD_ENCRYPTION_KEY = 'sua_chave_fernet_32_bytes', SECRET_KEY = 'sua_django_secret_key', DEBUG = True

# Testando a API com Insomnia: 
- Registrar usuário: POST /api/usuarios/registro/
- Fazer login: POST /api/token/
- Usar token: Authorization: Bearer <token>
- Testar endpoints autenticados**

# Exemplo de Collection:
{
  "base_url": "http://127.0.0.1:8000",
  "endpoints": [
    "/api/token/",
    "/api/usuarios/registro/",
    "/api/pacientes/",
    "/api/profissionais/",
    "/api/agendamentos/",
    "/api/prontuarios/",
    "/api/exames/"
  ]
}

# Códigos de Status HTTP:
- 200 OK: Requisição bem-sucedida
- 201 Created: Recurso criado com sucesso
- 400 Bad Request: Dados inválidos
- 401 Unauthorized: Token inválido ou ausente
- 403 Forbidden: Acesso negado
- 404 Not Found: Recurso não encontrado
- 500 Internal Server Error: Erro no servidor

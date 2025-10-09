from django.contrib.auth.models import AbstractUser
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

class CustomUser(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('P', 'Paciente'),
        ('M', 'Médico'),
        ('A', 'Administrador'),
    )
    
    tipo_usuario = models.CharField(max_length=1, choices=TIPO_USUARIO_CHOICES, default='P')
    
    # Campos criptografados - DADOS SENSÍVEIS (LGPD)
    cpf = EncryptedCharField(max_length=14, unique=True, null=True, blank=True)
    telefone = EncryptedCharField(max_length=20, null=True, blank=True)
    data_nascimento = EncryptedCharField(max_length=10, null=True, blank=True)
    
    # Campos normais (não sensíveis)
    crm = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"

class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado'),
    )
    
    TIPO_CONSULTA_CHOICES = (
        ('presencial', 'Presencial'),
        ('telemedicina', 'Telemedicina'),
    )
    
    # Relacionamentos
    paciente = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'P'},
        related_name='agendamentos_paciente'
    )
    
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'M'}, 
        related_name='agendamentos_medico'
    )
    
    # Campos do agendamento
    data_agendamento = models.DateTimeField()
    duracao_minutos = models.IntegerField(default=30)
    tipo_consulta = models.CharField(max_length=12, choices=TIPO_CONSULTA_CHOICES, default='presencial')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendado')
    
    # Campos para telemedicina
    link_consulta = models.URLField(blank=True, null=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_agendamento']
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
    
    def __str__(self):
        return f"{self.paciente.username} com {self.medico.username} - {self.data_agendamento}"

class Prontuario(models.Model):
    TIPO_ANOTACAO_CHOICES = (
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
        ('diagnostico', 'Diagnóstico'),
        ('prescricao', 'Prescrição'),
        ('evolucao', 'Evolução'),
    )
    
    # Relacionamentos
    paciente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'P'},
        related_name='prontuarios_paciente'
    )
    
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'M'},
        related_name='prontuarios_medico'
    )
    
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prontuarios'
    )
    
    # Campos do prontuário
    tipo_anotacao = models.CharField(max_length=15, choices=TIPO_ANOTACAO_CHOICES, default='consulta')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    sintomas = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    prescricao_medicamentos = models.TextField(blank=True)
    exames_solicitados = models.TextField(blank=True)
    
    # Campos vitais (criptografados)
    pressao_arterial = EncryptedCharField(max_length=20, blank=True)
    temperatura = EncryptedCharField(max_length=10, blank=True)
    frequencia_cardiaca = EncryptedCharField(max_length=10, blank=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
    
    def __str__(self):
        return f"Prontuário {self.paciente.username} - {self.titulo}"

class Exame(models.Model):
    TIPO_EXAME_CHOICES = (
        ('sangue', 'Exame de Sangue'),
        ('urina', 'Exame de Urina'),
        ('imagem', 'Exame de Imagem'),
        ('cardiologico', 'Exame Cardiológico'),
        ('neurologico', 'Exame Neurológico'),
        ('outros', 'Outros'),
    )
    
    STATUS_EXAME_CHOICES = (
        ('solicitado', 'Solicitado'),
        ('coletado', 'Coletado'),
        ('processando', 'Processando'),
        ('finalizado', 'Finalizado'),
        ('entregue', 'Entregue'),
    )
    
    # Relacionamentos
    paciente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'P'},
        related_name='exames_paciente'
    )
    
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'M'},
        related_name='exames_medico'
    )
    
    # Informações do exame
    tipo_exame = models.CharField(max_length=20, choices=TIPO_EXAME_CHOICES)
    nome_exame = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    # Resultados (criptografados - dados sensíveis)
    resultado = EncryptedCharField(blank=True)
    observacoes = EncryptedCharField(blank=True)
    valores_referencia = EncryptedCharField(blank=True)
    
    # Datas importantes
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_realizacao = models.DateField(null=True, blank=True)
    data_resultado = models.DateTimeField(null=True, blank=True)
    
    # Status e local
    status = models.CharField(max_length=15, choices=STATUS_EXAME_CHOICES, default='solicitado')
    laboratorio = models.CharField(max_length=200, blank=True)
    
    # Arquivos (opcional - para resultados em PDF/imagem)
    # arquivo_resultado = models.FileField(upload_to='exames/', null=True, blank=True)
    
    class Meta:
        ordering = ['-data_solicitacao']
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
    
    def __str__(self):
        return f"Exame {self.nome_exame} - {self.paciente.username}"

class Exame(models.Model):
    TIPO_EXAME_CHOICES = (
        ('sangue', 'Exame de Sangue'),
        ('urina', 'Exame de Urina'),
        ('imagem', 'Exame de Imagem'),
        ('cardiologico', 'Exame Cardiológico'),
        ('neurologico', 'Exame Neurológico'),
        ('outros', 'Outros'),
    )
    
    STATUS_EXAME_CHOICES = (
        ('solicitado', 'Solicitado'),
        ('coletado', 'Coletado'),
        ('processando', 'Processando'),
        ('finalizado', 'Finalizado'),
        ('entregue', 'Entregue'),
    )
    
    # Relacionamentos
    paciente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'P'},
        related_name='exames_paciente'
    )
    
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'M'},
        related_name='exames_medico'
    )
    
    # Informações do exame
    tipo_exame = models.CharField(max_length=20, choices=TIPO_EXAME_CHOICES)
    nome_exame = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    # Resultados (criptografados - dados sensíveis)
    resultado = EncryptedCharField(blank=True)
    observacoes = EncryptedCharField(blank=True)
    valores_referencia = EncryptedCharField(blank=True)
    
    # Datas importantes
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_realizacao = models.DateField(null=True, blank=True)
    data_resultado = models.DateTimeField(null=True, blank=True)
    
    # Status e local
    status = models.CharField(max_length=15, choices=STATUS_EXAME_CHOICES, default='solicitado')
    laboratorio = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-data_solicitacao']
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
    
    def __str__(self):
        return f"Exame {self.nome_exame} - {self.paciente.username}"
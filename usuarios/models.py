from django.contrib.auth.models import AbstractUser
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.utils import timezone

class CustomUser(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('P', 'Paciente'),
        ('M', 'Médico'),
        ('A', 'Administrador'),
    )
    
    tipo_usuario = models.CharField(max_length=1, choices=TIPO_USUARIO_CHOICES, default='P')
    
    #Campos criptografados 
    cpf = EncryptedCharField(max_length=14, unique=True, null=True, blank=True)
    telefone = EncryptedCharField(max_length=20, null=True, blank=True)
    data_nascimento = EncryptedCharField(max_length=10, null=True, blank=True)
    
    #Campos normais
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
    
    #Agendamento
    data_agendamento = models.DateTimeField()
    duracao_minutos = models.IntegerField(default=30)
    tipo_consulta = models.CharField(max_length=12, choices=TIPO_CONSULTA_CHOICES, default='presencial')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendado')
    motivo_cancelamento = models.TextField(blank=True, null=True)
    data_cancelamento = models.DateTimeField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    #Telemedicina
    link_consulta = models.URLField(blank=True, null=True)
    
    #Auditoria
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
    
    #Prontuário
    tipo_anotacao = models.CharField(max_length=15, choices=TIPO_ANOTACAO_CHOICES, default='consulta')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    sintomas = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    prescricao_medicamentos = models.TextField(blank=True)
    exames_solicitados = models.TextField(blank=True)
    
    #Informações de saude
    pressao_arterial = EncryptedCharField(max_length=20, blank=True)
    temperatura = EncryptedCharField(max_length=10, blank=True)
    frequencia_cardiaca = EncryptedCharField(max_length=10, blank=True)
    
 
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
    
    #Informações do exame
    tipo_exame = models.CharField(max_length=20, choices=TIPO_EXAME_CHOICES)
    nome_exame = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    #Resultados (criptografados)
    resultado = EncryptedCharField(blank=True)
    observacoes = EncryptedCharField(blank=True)
    valores_referencia = EncryptedCharField(blank=True)
    
    #Datas
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_realizacao = models.DateField(null=True, blank=True)
    data_resultado = models.DateTimeField(null=True, blank=True)
    
    #Status 
    status = models.CharField(max_length=15, choices=STATUS_EXAME_CHOICES, default='solicitado')
    laboratorio = models.CharField(max_length=200, blank=True)

    
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
    
    #Informações do exame
    tipo_exame = models.CharField(max_length=20, choices=TIPO_EXAME_CHOICES)
    nome_exame = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    #Resultados
    resultado = EncryptedCharField(blank=True)
    observacoes = EncryptedCharField(blank=True)
    valores_referencia = EncryptedCharField(blank=True)
    
    #Datas import
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_realizacao = models.DateField(null=True, blank=True)
    data_resultado = models.DateTimeField(null=True, blank=True)
    
    #Status
    status = models.CharField(max_length=15, choices=STATUS_EXAME_CHOICES, default='solicitado')
    laboratorio = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-data_solicitacao']
        verbose_name = 'Exame'
        verbose_name_plural = 'Exames'
    
    def __str__(self):
        return f"Exame {self.nome_exame} - {self.paciente.username}"
    
class Receita(models.Model):
    TIPOS_RECEITA = [
        ('medicamento', 'Medicamento'),
        ('exame', 'Exame'),
        ('procedimento', 'Procedimento'),
        ('dieta', 'Dieta'),
    ]
    
    STATUS_RECEITA = [
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa'),
        ('finalizada', 'Finalizada'),
    ]
    
    paciente = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='receitas_paciente',
        limit_choices_to={'tipo_usuario': 'P'}
    )
    medico = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='receitas_medico',
        limit_choices_to={'tipo_usuario': 'M'}
    )
    tipo = models.CharField(max_length=20, choices=TIPOS_RECEITA, default='medicamento')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    
    #Para medicamentos
    medicamentos = models.TextField(blank=True, null=True, help_text="Lista de medicamentos, dosagens e posologias")
    posologia = models.TextField(blank=True, null=True, help_text="Instruções de uso detalhadas")
    
    #Para exames/procedimentos
    exames_solicitados = models.TextField(blank=True, null=True, help_text="Exames ou procedimentos solicitados")
    
    #Controle de validade
    data_prescricao = models.DateTimeField(auto_now_add=True)
    data_validade = models.DateField(help_text="Data até quando a receita é válida")
    
    #Status
    status = models.CharField(max_length=20, choices=STATUS_RECEITA, default='ativa')
    observacoes = models.TextField(blank=True, null=True)
 
    prontuario = models.ForeignKey(
        'Prontuario', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='receitas'
    )
    
    #Campos de controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios_receita'
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        ordering = ['-data_prescricao']
    
    def __str__(self):
        return f"Receita {self.id} - {self.paciente.username} - {self.medico.username}"
    
    def esta_valida(self):
    
        from django.utils import timezone
        return self.data_validade >= timezone.now().date() and self.status == 'ativa'
    
    def suspender(self):
        self.status = 'suspensa'
        self.save()
    
    def finalizar(self):
        self.status = 'finalizada'
        self.save()
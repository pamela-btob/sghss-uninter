from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import CustomUser, Agendamento, Prontuario, Receita
from .models import Exame

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'tipo_usuario', 'cpf', 'data_nascimento', 'telefone', 'crm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class AgendamentoSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source='paciente.username', read_only=True)
    medico_nome = serializers.CharField(source='medico.username', read_only=True)
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'paciente', 'medico', 'paciente_nome', 'medico_nome',
            'data_agendamento', 'duracao_minutos', 'tipo_consulta', 
            'status', 'link_consulta', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'paciente_nome', 'medico_nome']
    
    def validate(self, data):
        if data['data_agendamento'] <= timezone.now():
            raise serializers.ValidationError("A data do agendamento deve ser no futuro.")
        
        if data['paciente'] == data['medico']:
            raise serializers.ValidationError("Paciente e médico não podem ser a mesma pessoa.")
        
        return data
class ProntuarioSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source='paciente.username', read_only=True)
    medico_nome = serializers.CharField(source='medico.username', read_only=True)
    agendamento_data = serializers.DateTimeField(source='agendamento.data_agendamento', read_only=True)
    
    class Meta:
        model = Prontuario
        fields = [
            'id', 'paciente', 'medico', 'agendamento', 'paciente_nome', 'medico_nome', 'agendamento_data',
            'tipo_anotacao', 'titulo', 'descricao', 'sintomas', 'diagnostico', 
            'prescricao_medicamentos', 'exames_solicitados', 'pressao_arterial',
            'temperatura', 'frequencia_cardiaca', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'paciente_nome', 'medico_nome', 'agendamento_data']
    
    def validate(self, data):
        #Verifica se o médico tem permissão para acessar este paciente
        if data['paciente'].tipo_usuario != 'P':
            raise serializers.ValidationError("Você não tem permissão")
        
        if data['medico'].tipo_usuario != 'M':
            raise serializers.ValidationError("Você não tem permissão")
        
        return data

class ExameSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source='paciente.username', read_only=True)
    medico_nome = serializers.CharField(source='medico.username', read_only=True)
    
    class Meta:
        model = Exame
        fields = [
            'id', 'paciente', 'medico', 'paciente_nome', 'medico_nome',
            'tipo_exame', 'nome_exame', 'descricao', 'resultado',
            'observacoes', 'valores_referencia', 'data_solicitacao',
            'data_realizacao', 'data_resultado', 'status', 'laboratorio'
        ]
        read_only_fields = ['id', 'data_solicitacao', 'paciente_nome', 'medico_nome']
    
    def validate(self, data):
        if data.get('data_realizacao') and data['data_realizacao'] < timezone.now().date():
            raise serializers.ValidationError("A data de realização não pode ser anterior a data atual.")
        
        if (data.get('data_realizacao') and data.get('data_resultado') and 
            data['data_resultado'].date() < data['data_realizacao']):
            raise serializers.ValidationError("A data do resultado deve ser após a data de realização do exame.")
        
        return data
    
class ReceitaSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source='paciente.get_full_name', read_only=True)
    medico_nome = serializers.CharField(source='medico.get_full_name', read_only=True)
    esta_valida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Receita
        fields = [
            'id',
            'paciente', 'paciente_nome',
            'medico', 'medico_nome',
            'tipo', 'titulo', 'descricao',
            'medicamentos', 'posologia',
            'exames_solicitados',
            'data_prescricao', 'data_validade',
            'status', 'observacoes',
            'prontuario', 'esta_valida',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['data_prescricao', 'criado_em', 'atualizado_em']
    
    def validate_data_validade(self, value):
        
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("A data não pode ser anterior a data atual.")
        return value
    
    def validate(self, data):
        
        #Verificar se médico ou paciente está solicitando
        if data.get('medico') and data['medico'].tipo_usuario != 'M':
            raise serializers.ValidationError({"medico": "O prescritor deve ser um médico."})
        
        if data.get('paciente') and data['paciente'].tipo_usuario != 'P':
            raise serializers.ValidationError({"paciente": "O destinatário deve ser um paciente."})
        
        return data
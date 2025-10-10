from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def enviar_email_notificacao(assunto, template, contexto, destinatarios):
    try:
        html_message = render_to_string(template, contexto)
        plain_message = strip_tags(html_message)
        
        #Envia o email
        send_mail(
            assunto,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def notificar_agendamento_criado(agendamento):
    contexto = {
        'paciente_nome': agendamento.paciente.get_full_name() or agendamento.paciente.username,
        'medico_nome': agendamento.medico.get_full_name() or agendamento.medico.username,
        'data_agendamento': agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M'),
        'tipo_consulta': agendamento.get_tipo_consulta_display(),
        'local': 'Consultório' if agendamento.tipo_consulta == 'presencial' else 'Online',
        'agendamento_id': agendamento.id,
    }
    
    assunto = f"Confirmação de Agendamento - {agendamento.id}"
    
    return enviar_email_notificacao(
        assunto,
        'emails/agendamento_criado.html',
        contexto,
        [agendamento.paciente.email]
    )

def notificar_agendamento_cancelado(agendamento, motivo=None):
    contexto = {
        'paciente_nome': agendamento.paciente.get_full_name() or agendamento.paciente.username,
        'medico_nome': agendamento.medico.get_full_name() or agendamento.medico.username,
        'data_agendamento': agendamento.data_agendamento.strftime('%d/%m/%Y às %H:%M'),
        'motivo_cancelamento': motivo or 'Cancelado pelo sistema',
        'agendamento_id': agendamento.id,
    }
    
    assunto = f"Cancelamento de Agendamento - {agendamento.id}"
    
    return enviar_email_notificacao(
        assunto,
        'emails/agendamento_cancelado.html',
        contexto,
        [agendamento.paciente.email, agendamento.medico.email]
    )

def notificar_receita_criada(receita):
    contexto = {
        'paciente_nome': receita.paciente.get_full_name() or receita.paciente.username,
        'medico_nome': receita.medico.get_full_name() or receita.medico.username,
        'titulo_receita': receita.titulo,
        'tipo_receita': receita.get_tipo_display(),
        'data_validade': receita.data_validade.strftime('%d/%m/%Y'),
        'descricao': receita.descricao,
        'receita_id': receita.id,
    }
    
    assunto = f"Nova Receita - {receita.titulo}"
    
    return enviar_email_notificacao(
        assunto,
        'emails/receita_criada.html',
        contexto,
        [receita.paciente.email]
    )
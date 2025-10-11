from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from .models import CustomUser, Agendamento, Prontuario, Exame, Receita
from .serializers import (
    UserRegistrationSerializer,
    AgendamentoSerializer,
    ProntuarioSerializer,
    ExameSerializer,
    ReceitaSerializer,
)
from .notifications import (
    notificar_agendamento_criado,
    notificar_agendamento_cancelado,
    notificar_receita_criada,
)


def frontend_index(request):
    return render(request, 'frontend/index.html')

# Registrar o usuaário
@api_view(["POST"])
def user_registration(request):
    if request.method == "POST":
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuário criado com sucesso!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Perfil do usuário
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response(
        {
            "username": user.username,
            "email": user.email,
            "tipo_usuario": user.tipo_usuario,
            "message": "Você está autenticado!",
        }
    )


# Lista e cria os agendamentos
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def agendamento_list_create(request):
    if request.method == "GET":
        if request.user.tipo_usuario == "P":
            agendamentos = Agendamento.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == "M":
            agendamentos = Agendamento.objects.filter(medico=request.user)
        else:
            agendamentos = Agendamento.objects.all()

        serializer = AgendamentoSerializer(agendamentos, many=True)
        return Response(serializer.data)

    elif request.method == "POST":

        data = request.data.copy()
        data["medico"] = request.user.id

        serializer = AgendamentoSerializer(data=data)
        if serializer.is_valid():
            agendamento = serializer.save()

            # Notifica o agendameto criado
            try:
                notificar_agendamento_criado(agendamento)
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalehes do agendamento
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def agendamento_detail(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)
    except Agendamento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if (
        request.user != agendamento.paciente
        and request.user != agendamento.medico
        and request.user.tipo_usuario != "A"
    ):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = AgendamentoSerializer(agendamento)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = AgendamentoSerializer(agendamento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        agendamento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Cancela o agendamento
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancelar_agendamento(request, pk):
    try:
        agendamento = Agendamento.objects.get(pk=pk)

        user = request.user
        pode_cancelar = (
            user.tipo_usuario == "A"
            or (user.tipo_usuario == "P" and agendamento.paciente == user)
            or (user.tipo_usuario == "M" and agendamento.medico == user)
        )
        # confirma o cancelamento conforme o usuário
        if not pode_cancelar:
            return Response(
                {"error": "Você não tem permissão para cancelar este agendamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if agendamento.status == "cancelado":
            return Response(
                {"error": "Este agendamento já está cancelado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agendamento.status = "cancelado"
        agendamento.motivo_cancelamento = request.data.get(
            "motivo", "Cancelado pelo usuário"
        )
        agendamento.data_cancelamento = timezone.now()
        agendamento.save()

        # Notificação de cancelamento
        try:
            notificar_agendamento_cancelado(
                agendamento, agendamento.motivo_cancelamento
            )
        except Exception as e:
            print(f"Erro ao enviar notificação de cancelamento: {e}")

        serializer = AgendamentoSerializer(agendamento)

        return Response(
            {
                "message": "Agendamento cancelado com sucesso.",
                "agendamento": serializer.data,
            }
        )

    except Agendamento.DoesNotExist:
        return Response(
            {"error": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


# Criação de prontuários
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def prontuario_list_create(request):
    if request.method == "GET":
        if request.user.tipo_usuario == "P":
            prontuarios = Prontuario.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == "M":
            prontuarios = Prontuario.objects.filter(medico=request.user)
        else:
            prontuarios = Prontuario.objects.all()

        serializer = ProntuarioSerializer(prontuarios, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if request.user.tipo_usuario != "M":
            return Response(
                {"error": "Apenas médicos podem criar prontuários."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["medico"] = request.user.id

        serializer = ProntuarioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def prontuario_detail(request, pk):
    try:
        prontuario = Prontuario.objects.get(pk=pk)
    except Prontuario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if (
        request.user != prontuario.paciente
        and request.user != prontuario.medico
        and request.user.tipo_usuario != "A"
    ):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = ProntuarioSerializer(prontuario)
        return Response(serializer.data)

    elif request.method == "PUT":
        if request.user != prontuario.medico:
            return Response(
                {"error": "Apenas o médico responsável pode editar o prontuário."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProntuarioSerializer(prontuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Requisição de exames
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def exame_list_create(request):
    if request.method == "GET":
        if request.user.tipo_usuario == "P":
            exames = Exame.objects.filter(paciente=request.user)
        elif request.user.tipo_usuario == "M":
            exames = Exame.objects.filter(medico=request.user)
        else:
            exames = Exame.objects.all()

        serializer = ExameSerializer(exames, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if request.user.tipo_usuario != "M":
            return Response(
                {"error": "Apenas médicos podem solicitar exames."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["medico"] = request.user.id

        serializer = ExameSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def exame_detail(request, pk):
    try:
        exame = Exame.objects.get(pk=pk)
    except Exame.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if (
        request.user != exame.paciente
        and request.user != exame.medico
        and request.user.tipo_usuario != "A"
    ):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = ExameSerializer(exame)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if request.user.tipo_usuario == "P":
            return Response(
                {"error": "Pacientes não podem editar exames."},
                status=status.HTTP_403_FORBIDDEN,
            )

        partial = request.method == "PATCH"
        serializer = ExameSerializer(exame, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Dashboard do administrador
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_estatisticas(request):
    if request.user.tipo_usuario != "A":
        return Response(
            {"error": "Apenas administradores podem acessar o dashboard."},
            status=status.HTTP_403_FORBIDDEN,
        )

    total_usuarios = CustomUser.objects.count()
    total_pacientes = CustomUser.objects.filter(tipo_usuario="P").count()
    total_medicos = CustomUser.objects.filter(tipo_usuario="M").count()
    total_administradores = CustomUser.objects.filter(tipo_usuario="A").count()

    total_agendamentos = Agendamento.objects.count()
    agendamentos_hoje = Agendamento.objects.filter(
        data_agendamento__date=timezone.now().date()
    ).count()
    agendamentos_mes = Agendamento.objects.filter(
        data_agendamento__month=timezone.now().month,
        data_agendamento__year=timezone.now().year,
    ).count()

    agendamentos_agendados = Agendamento.objects.filter(status="agendado").count()
    agendamentos_confirmados = Agendamento.objects.filter(status="confirmado").count()
    agendamentos_realizados = Agendamento.objects.filter(status="realizado").count()
    agendamentos_cancelados = Agendamento.objects.filter(status="cancelado").count()

    total_prontuarios = Prontuario.objects.count()
    prontuarios_mes = Prontuario.objects.filter(
        criado_em__month=timezone.now().month, criado_em__year=timezone.now().year
    ).count()

    total_exames = Exame.objects.count()
    exames_solicitados = Exame.objects.filter(status="solicitado").count()
    exames_finalizados = Exame.objects.filter(status="finalizado").count()

    consultas_presencial = Agendamento.objects.filter(
        tipo_consulta="presencial"
    ).count()
    consultas_telemedicina = Agendamento.objects.filter(
        tipo_consulta="telemedicina"
    ).count()

    exames_mais_solicitados = (
        Exame.objects.values("tipo_exame")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    dados = {
        "usuarios": {
            "total": total_usuarios,
            "pacientes": total_pacientes,
            "medicos": total_medicos,
            "administradores": total_administradores,
        },
        "agendamentos": {
            "total": total_agendamentos,
            "hoje": agendamentos_hoje,
            "este_mes": agendamentos_mes,
            "por_status": {
                "agendados": agendamentos_agendados,
                "confirmados": agendamentos_confirmados,
                "realizados": agendamentos_realizados,
                "cancelados": agendamentos_cancelados,
            },
            "por_tipo": {
                "presencial": consultas_presencial,
                "telemedicina": consultas_telemedicina,
            },
        },
        "prontuarios": {"total": total_prontuarios, "este_mes": prontuarios_mes},
        "exames": {
            "total": total_exames,
            "solicitados": exames_solicitados,
            "finalizados": exames_finalizados,
            "mais_solicitados": list(exames_mais_solicitados),
        },
        "metadados": {"data_geracao": timezone.now(), "periodo": "todo o período"},
    }

    return Response(dados)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def relatorio_agendamentos(request):
    if request.user.tipo_usuario != "A":
        return Response(
            {"error": "Apenas administradores podem acessar relatórios."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    medico_id = request.GET.get("medico_id")
    status_agendamento = request.GET.get("status")

    agendamentos = Agendamento.objects.all()

    if data_inicio:
        agendamentos = agendamentos.filter(data_agendamento__date__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data_agendamento__date__lte=data_fim)
    if medico_id:
        agendamentos = agendamentos.filter(medico_id=medico_id)
    if status_agendamento:
        agendamentos = agendamentos.filter(status=status_agendamento)

    serializer = AgendamentoSerializer(agendamentos, many=True)

    total = agendamentos.count()
    por_status = agendamentos.values("status").annotate(total=Count("id"))
    por_tipo = agendamentos.values("tipo_consulta").annotate(total=Count("id"))

    relatorio = {
        "dados": serializer.data,
        "estatisticas": {
            "total": total,
            "por_status": list(por_status),
            "por_tipo_consulta": list(por_tipo),
        },
        "filtros_aplicados": {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "medico_id": medico_id,
            "status": status_agendamento,
        },
    }

    return Response(relatorio)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def relatorio_financeiro(request):
    if request.user.tipo_usuario != "A":
        return Response(
            {"error": "Apenas administradores podem acessar relatórios financeiros."},
            status=status.HTTP_403_FORBIDDEN,
        )

    receita_mensal = {
        "consultas_presencial": 150 * 120.00,
        "consultas_telemedicina": 80 * 80.00,
        "exames": 45 * 50.00,
        "total": (150 * 120.00) + (80 * 80.00) + (45 * 50.00),
    }

    despesas_mensais = {
        "folha_pagamento": 25000.00,
        "manutencao_equipamentos": 5000.00,
        "suprimentos": 3000.00,
        "total": 25000.00 + 5000.00 + 3000.00,
    }

    lucro_mensal = receita_mensal["total"] - despesas_mensais["total"]

    relatorio_financeiro = {
        "receitas": receita_mensal,
        "despesas": despesas_mensais,
        "lucro_liquido": lucro_mensal,
        "margem_lucro": (
            (lucro_mensal / receita_mensal["total"]) * 100
            if receita_mensal["total"] > 0
            else 0
        ),
        "periodo": f"{timezone.now().strftime('%B %Y')} (dados simulados)",
        "observacao": "Este é um relatório demonstrativo com dados simulados para fins de demonstração do sistema.",
    }

    return Response(relatorio_financeiro)


# Histórico do paciente
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historico_paciente(request, paciente_id=None):
    user = request.user

    try:
        if paciente_id:
            if user.tipo_usuario not in ["A", "M"]:
                return Response(
                    {
                        "error": "Apenas administradores e médicos podem visualizar histórico de outros pacientes."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                paciente = CustomUser.objects.get(id=paciente_id)
                if paciente.tipo_usuario != "P":
                    return Response(
                        {"error": "O ID especificado não pertence a um paciente."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "Paciente não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            if user.tipo_usuario != "P":
                return Response(
                    {
                        "error": "Apenas pacientes podem visualizar próprio histórico sem especificar ID."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            paciente = user

        paciente_data = {
            "id": paciente.id,
            "nome": paciente.get_full_name() or paciente.username,
            "email": paciente.email,
            "data_cadastro": paciente.date_joined,
            "tipo_usuario": paciente.get_tipo_usuario_display(),
            "tipo_sanguineo": getattr(paciente, "tipo_sanguineo", "Não informado"),
            "alergias": getattr(paciente, "alergias", "Não informado"),
        }

        prontuarios = Prontuario.objects.filter(paciente=paciente).order_by(
            "-criado_em"
        )
        prontuarios_data = ProntuarioSerializer(prontuarios, many=True).data

        exames = Exame.objects.filter(paciente=paciente).order_by("-data_solicitacao")
        exames_data = ExameSerializer(exames, many=True).data

        trinta_dias_atras = timezone.now() - timedelta(days=30)
        agendamentos = Agendamento.objects.filter(
            paciente=paciente, data_agendamento__gte=trinta_dias_atras
        ).order_by("-data_agendamento")
        agendamentos_data = AgendamentoSerializer(agendamentos, many=True).data

        total_consultas = Agendamento.objects.filter(
            paciente=paciente, status="realizado"
        ).count()

        total_exames = Exame.objects.filter(paciente=paciente).count()

        consultas_presencial = Agendamento.objects.filter(
            paciente=paciente, tipo_consulta="presencial", status="realizado"
        ).count()

        consultas_telemedicina = Agendamento.objects.filter(
            paciente=paciente, tipo_consulta="telemedicina", status="realizado"
        ).count()

        exames_solicitados = Exame.objects.filter(
            paciente=paciente, status="solicitado"
        ).count()

        exames_finalizados = Exame.objects.filter(
            paciente=paciente, status="finalizado"
        ).count()

        historico = {
            "paciente": paciente_data,
            "estatisticas": {
                "total_consultas": total_consultas,
                "total_exames": total_exames,
                "consultas_presencial": consultas_presencial,
                "consultas_telemedicina": consultas_telemedicina,
                "exames_solicitados": exames_solicitados,
                "exames_finalizados": exames_finalizados,
            },
            "prontuarios": prontuarios_data,
            "exames": exames_data,
            "agendamentos_recentes": agendamentos_data,
            "metadados": {
                "data_consulta": timezone.now(),
                "periodo_agendamentos": "últimos 30 dias",
                "total_prontuarios": len(prontuarios_data),
                "total_exames": len(exames_data),
                "visualizado_por": user.username,
                "tipo_visualizador": user.get_tipo_usuario_display(),
            },
        }

        return Response(historico)

    except Exception as e:
        return Response(
            {"error": f"Erro ao gerar histórico: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Receitas médicas
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def receita_list_create(request):
    if request.method == "GET":
        user = request.user

        if user.tipo_usuario == "P":
            receitas = Receita.objects.filter(paciente=user)
        elif user.tipo_usuario == "M":
            receitas = Receita.objects.filter(medico=user)
        elif user.tipo_usuario == "A":
            receitas = Receita.objects.all()
        else:
            return Response(
                {"error": "Tipo de usuário não permitido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        status_filter = request.GET.get("status")
        tipo_filter = request.GET.get("tipo")
        paciente_filter = request.GET.get("paciente_id")

        if status_filter:
            receitas = receitas.filter(status=status_filter)
        if tipo_filter:
            receitas = receitas.filter(tipo=tipo_filter)
        if paciente_filter and user.tipo_usuario in ["M", "A"]:
            receitas = receitas.filter(paciente_id=paciente_filter)

        receitas = receitas.order_by("-data_prescricao")

        serializer = ReceitaSerializer(receitas, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if request.user.tipo_usuario != "M":
            return Response(
                {"error": "Apenas médicos podem criar receitas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReceitaSerializer(data=request.data)
        if serializer.is_valid():
            receita = serializer.save(medico=request.user)

            try:
                notificar_receita_criada(receita)
            except Exception as e:
                print(f"Erro ao enviar notificação de receita: {e}")

            return Response(
                ReceitaSerializer(receita).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def receita_detail(request, pk):
    try:
        receita = Receita.objects.get(pk=pk)
    except Receita.DoesNotExist:
        return Response(
            {"error": "Receita não encontrada."}, status=status.HTTP_404_NOT_FOUND
        )

    user = request.user
    pode_acessar = (
        user.tipo_usuario == "A" or receita.medico == user or receita.paciente == user
    )

    if not pode_acessar:
        return Response(
            {"error": "Você não tem permissão para acessar esta receita."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        serializer = ReceitaSerializer(receita)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if user.tipo_usuario not in ["A", "M"] or (
            user.tipo_usuario == "M" and receita.medico != user
        ):
            return Response(
                {
                    "error": "Apenas o médico prescritor ou administradores podem editar receitas."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReceitaSerializer(
            receita, data=request.data, partial=request.method == "PATCH"
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if user.tipo_usuario != "A":
            return Response(
                {"error": "Apenas administradores podem deletar receitas."},
                status=status.HTTP_403_FORBIDDEN,
            )
        receita.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def suspender_receita(request, pk):
    try:
        receita = Receita.objects.get(pk=pk)
    except Receita.DoesNotExist:
        return Response(
            {"error": "Receita não encontrada."}, status=status.HTTP_404_NOT_FOUND
        )

    user = request.user
    pode_suspender = user.tipo_usuario == "A" or (
        user.tipo_usuario == "M" and receita.medico == user
    )

    if not pode_suspender:
        return Response(
            {
                "error": "Apenas o médico prescritor ou administradores podem suspender receitas."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    receita.suspender()
    serializer = ReceitaSerializer(receita)
    return Response(
        {"message": "Receita suspensa com sucesso.", "receita": serializer.data}
    )
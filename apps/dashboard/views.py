import calendar
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from apps.clientes.models import Cliente
from apps.despesas.models import Despesa
from apps.estoque_insumos.models import Insumo
from apps.estoque_rodas.models import Roda
from apps.servicos.models import Servico
from apps.vendas.models import Venda


def usuario_tem_alguma_permissao(request):
    if request.user.is_superuser:
        return True

    permissoes = getattr(request, "rg_permissoes", None)

    if not permissoes:
        return False

    campos = [
        "acesso_clientes",
        "acesso_estoque_rodas",
        "acesso_estoque_insumos",
        "acesso_servicos",
        "acesso_vendas",
        "acesso_despesas",
        "acesso_usuarios",
    ]

    return any(getattr(permissoes, campo, False) for campo in campos)


def usuario_pode_acessar(request, campo):
    if request.user.is_superuser:
        return True

    permissoes = getattr(request, "rg_permissoes", None)

    if not permissoes:
        return False

    return getattr(permissoes, campo, False)


def model_tem_campo(model, nome_campo):
    return any(campo.name == nome_campo for campo in model._meta.get_fields())


def primeiro_campo_existente(model, campos_possiveis):
    for campo in campos_possiveis:
        if model_tem_campo(model, campo):
            return campo

    return None


def somar_campo(queryset, model, campos_possiveis):
    campo = primeiro_campo_existente(model, campos_possiveis)

    if not campo:
        return Decimal("0.00")

    return queryset.aggregate(total=Sum(campo))["total"] or Decimal("0.00")


def formatar_moeda(valor):
    if valor is None:
        valor = Decimal("0.00")

    valor = Decimal(valor)

    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")

    return f"R$ {texto}"


def nome_mes_abreviado(numero_mes):
    nomes = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez",
    }

    return nomes.get(numero_mes, "")


def limpar_ano(valor, ano_padrao):
    try:
        ano = int(valor)
    except (TypeError, ValueError):
        return ano_padrao

    if ano < 2000 or ano > ano_padrao + 1:
        return ano_padrao

    return ano


def limpar_mes(valor):
    try:
        mes = int(valor)
    except (TypeError, ValueError):
        return None

    if mes < 1 or mes > 12:
        return None

    return mes


def montar_opcoes_anos():
    ano_atual = date.today().year
    return list(range(ano_atual, ano_atual - 6, -1))


def montar_opcoes_meses():
    return [
        {"value": 1, "label": "Janeiro"},
        {"value": 2, "label": "Fevereiro"},
        {"value": 3, "label": "Março"},
        {"value": 4, "label": "Abril"},
        {"value": 5, "label": "Maio"},
        {"value": 6, "label": "Junho"},
        {"value": 7, "label": "Julho"},
        {"value": 8, "label": "Agosto"},
        {"value": 9, "label": "Setembro"},
        {"value": 10, "label": "Outubro"},
        {"value": 11, "label": "Novembro"},
        {"value": 12, "label": "Dezembro"},
    ]


def montar_labels_periodo(ano, mes=None):
    if mes:
        total_dias = calendar.monthrange(ano, mes)[1]
        labels = [f"{dia:02d}" for dia in range(1, total_dias + 1)]
        return labels

    return [nome_mes_abreviado(mes_numero) for mes_numero in range(1, 13)]


def somar_por_periodo(queryset, model, campos_data_possiveis, campos_valor_possiveis, ano, mes=None):
    campo_data = primeiro_campo_existente(model, campos_data_possiveis)
    campo_valor = primeiro_campo_existente(model, campos_valor_possiveis)

    labels = montar_labels_periodo(ano, mes)

    if not campo_data or not campo_valor:
        return [0 for _ in labels]

    dados = []

    if mes:
        total_dias = calendar.monthrange(ano, mes)[1]

        for dia in range(1, total_dias + 1):
            filtros = {
                f"{campo_data}__year": ano,
                f"{campo_data}__month": mes,
                f"{campo_data}__day": dia,
            }

            total = queryset.filter(**filtros).aggregate(
                total=Sum(campo_valor)
            )["total"] or Decimal("0.00")

            dados.append(float(total))

        return dados

    for mes_numero in range(1, 13):
        filtros = {
            f"{campo_data}__year": ano,
            f"{campo_data}__month": mes_numero,
        }

        total = queryset.filter(**filtros).aggregate(
            total=Sum(campo_valor)
        )["total"] or Decimal("0.00")

        dados.append(float(total))

    return dados


def somar_listas(lista_a, lista_b):
    tamanho = max(len(lista_a), len(lista_b))
    resultado = []

    for indice in range(tamanho):
        valor_a = lista_a[indice] if indice < len(lista_a) else 0
        valor_b = lista_b[indice] if indice < len(lista_b) else 0
        resultado.append(valor_a + valor_b)

    return resultado


def contar_por_periodo(queryset, model, campos_data_possiveis, ano, mes=None):
    campo_data = primeiro_campo_existente(model, campos_data_possiveis)

    labels = montar_labels_periodo(ano, mes)

    if not campo_data:
        return [0 for _ in labels]

    dados = []

    if mes:
        total_dias = calendar.monthrange(ano, mes)[1]

        for dia in range(1, total_dias + 1):
            filtros = {
                f"{campo_data}__year": ano,
                f"{campo_data}__month": mes,
                f"{campo_data}__day": dia,
            }

            dados.append(queryset.filter(**filtros).count())

        return dados

    for mes_numero in range(1, 13):
        filtros = {
            f"{campo_data}__year": ano,
            f"{campo_data}__month": mes_numero,
        }

        dados.append(queryset.filter(**filtros).count())

    return dados


def obter_choices_do_campo(model, nome_campo):
    try:
        campo = model._meta.get_field(nome_campo)
    except Exception:
        return {}

    return dict(campo.choices or [])


def montar_status_servicos():
    if not model_tem_campo(Servico, "status"):
        return {
            "labels": [],
            "data": [],
        }

    choices = obter_choices_do_campo(Servico, "status")

    registros = (
        Servico.objects
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    labels = []
    data = []

    for item in registros:
        status = item["status"]
        labels.append(choices.get(status, status or "Sem status"))
        data.append(item["total"])

    return {
        "labels": labels,
        "data": data,
    }


@login_required
def dashboard_home(request):
    if not usuario_tem_alguma_permissao(request):
        messages.info(
            request,
            "Seu usuário ainda não possui permissões de acesso. Solicite liberação ao administrador."
        )
        return redirect("usuarios:perfil")

    hoje = date.today()
    ano_atual = hoje.year

    ano_resumo = limpar_ano(request.GET.get("ano_resumo"), ano_atual)
    mes_resumo = limpar_mes(request.GET.get("mes_resumo"))

    ano_servicos = limpar_ano(request.GET.get("ano_servicos"), ano_atual)
    mes_servicos = limpar_mes(request.GET.get("mes_servicos"))

    pode_clientes = usuario_pode_acessar(request, "acesso_clientes")
    pode_estoque_rodas = usuario_pode_acessar(request, "acesso_estoque_rodas")
    pode_estoque_insumos = usuario_pode_acessar(request, "acesso_estoque_insumos")
    pode_servicos = usuario_pode_acessar(request, "acesso_servicos")
    pode_vendas = usuario_pode_acessar(request, "acesso_vendas")
    pode_despesas = usuario_pode_acessar(request, "acesso_despesas")

    total_clientes = Cliente.objects.count() if pode_clientes else 0

    total_rodas_cadastradas = 0
    total_rodas_estoque = 0
    rodas_baixo_estoque = []

    if pode_estoque_rodas:
        total_rodas_cadastradas = Roda.objects.count()
        total_rodas_estoque = Roda.objects.aggregate(
            total=Sum("quantidade")
        )["total"] or 0

        rodas_baixo_estoque = (
            Roda.objects
            .filter(quantidade__lte=2)
            .order_by("quantidade", "nome")[:5]
        )

    total_insumos_cadastrados = 0
    total_insumos_estoque = 0
    insumos_baixo_estoque = []

    if pode_estoque_insumos:
        total_insumos_cadastrados = Insumo.objects.count()
        total_insumos_estoque = Insumo.objects.aggregate(
            total=Sum("quantidade")
        )["total"] or 0

        insumos_baixo_estoque = (
            Insumo.objects
            .filter(quantidade__lte=2)
            .order_by("quantidade", "nome")[:5]
        )

    servicos_queryset = Servico.objects.all()
    vendas_queryset = Venda.objects.all()
    despesas_queryset = Despesa.objects.all()

    servicos_em_aberto = 0

    if pode_servicos:
        if model_tem_campo(Servico, "status"):
            servicos_em_aberto = servicos_queryset.exclude(
                status__in=[
                    "finalizado",
                    "finalizada",
                    "finalizada_aguardando_cliente",
                    "finalizada_entregue",
                    "cancelado",
                    "cancelada",
                ]
            ).count()
        else:
            servicos_em_aberto = servicos_queryset.count()

    vendas_mes = Decimal("0.00")
    servicos_mes = Decimal("0.00")
    receita_mes = Decimal("0.00")

    if pode_vendas:
        if model_tem_campo(Venda, "status"):
            vendas_queryset = vendas_queryset.exclude(
                status__in=["cancelado", "cancelada"]
            )

        campo_data_venda = primeiro_campo_existente(
            Venda,
            ["data_venda", "data_cadastro", "criado_em", "created_at"]
        )

        vendas_do_mes = vendas_queryset

        if campo_data_venda:
            vendas_do_mes = vendas_do_mes.filter(
                **{
                    f"{campo_data_venda}__year": hoje.year,
                    f"{campo_data_venda}__month": hoje.month,
                }
            )

        vendas_mes = somar_campo(
            vendas_do_mes,
            Venda,
            ["valor_total", "valor", "total"]
        )

    if pode_servicos:
        servicos_receita_queryset = servicos_queryset

        if model_tem_campo(Servico, "status"):
            servicos_receita_queryset = servicos_receita_queryset.exclude(
                status__in=["cancelado", "cancelada"]
            )

        campo_data_servico = primeiro_campo_existente(
            Servico,
            ["data_servico", "data_cadastro", "criado_em", "created_at"]
        )

        servicos_do_mes = servicos_receita_queryset

        if campo_data_servico:
            servicos_do_mes = servicos_do_mes.filter(
                **{
                    f"{campo_data_servico}__year": hoje.year,
                    f"{campo_data_servico}__month": hoje.month,
                }
            )

        servicos_mes = somar_campo(
            servicos_do_mes,
            Servico,
            ["valor_total", "valor", "total"]
        )

    receita_mes = vendas_mes + servicos_mes

    despesas_mes = Decimal("0.00")

    if pode_despesas:
        campo_data_despesa = primeiro_campo_existente(
            Despesa,
            ["data_vencimento", "data_despesa", "data_cadastro", "criado_em", "created_at"]
        )

        despesas_do_mes = despesas_queryset

        if campo_data_despesa:
            despesas_do_mes = despesas_do_mes.filter(
                **{
                    f"{campo_data_despesa}__year": hoje.year,
                    f"{campo_data_despesa}__month": hoje.month,
                }
            )

        despesas_mes = somar_campo(
            despesas_do_mes,
            Despesa,
            ["valor", "valor_total", "total"]
        )

    resumo_labels = montar_labels_periodo(ano_resumo, mes_resumo)
    servicos_labels = montar_labels_periodo(ano_servicos, mes_servicos)

    chart_vendas = [0 for _ in resumo_labels]
    chart_servicos_receita = [0 for _ in resumo_labels]
    chart_receitas = [0 for _ in resumo_labels]
    chart_despesas = [0 for _ in resumo_labels]
    chart_servicos = [0 for _ in servicos_labels]

    if pode_vendas:
        chart_vendas = somar_por_periodo(
            vendas_queryset,
            Venda,
            ["data_venda", "data_cadastro", "criado_em", "created_at"],
            ["valor_total", "valor", "total"],
            ano_resumo,
            mes_resumo
        )

    if pode_servicos:
        chart_servicos_receita = somar_por_periodo(
            servicos_queryset.exclude(status__in=["cancelado", "cancelada"]),
            Servico,
            ["data_servico", "data_cadastro", "criado_em", "created_at"],
            ["valor_total", "valor", "total"],
            ano_resumo,
            mes_resumo
        )

    chart_receitas = somar_listas(chart_vendas, chart_servicos_receita)

    if pode_despesas:
        chart_despesas = somar_por_periodo(
            despesas_queryset,
            Despesa,
            ["data_vencimento", "data_despesa", "data_cadastro", "criado_em", "created_at"],
            ["valor", "valor_total", "total"],
            ano_resumo,
            mes_resumo
        )

    if pode_servicos:
        chart_servicos = contar_por_periodo(
            servicos_queryset,
            Servico,
            ["data_servico", "data_cadastro", "criado_em", "created_at"],
            ano_servicos,
            mes_servicos
        )

    status_servicos = montar_status_servicos() if pode_servicos else {"labels": [], "data": []}

    estoque_labels = []
    estoque_data = []

    if pode_estoque_rodas:
        estoque_labels.append("Rodas")
        estoque_data.append(int(total_rodas_estoque))

    if pode_estoque_insumos:
        estoque_labels.append("Insumos")
        estoque_data.append(int(total_insumos_estoque))

    dashboard_charts = {
        "resumoLabels": resumo_labels,
        "resumoVendas": chart_receitas,
        "resumoDespesas": chart_despesas,

        "servicosLabels": servicos_labels,
        "servicosData": chart_servicos,

        "servicosStatusLabels": status_servicos["labels"],
        "servicosStatusData": status_servicos["data"],

        "estoqueLabels": estoque_labels,
        "estoqueData": estoque_data,
    }

    context = {
        "breadcrumbs": [
            {"label": "Painel"},
            {"label": "Dashboard"},
        ],

        "pode_clientes": pode_clientes,
        "pode_estoque_rodas": pode_estoque_rodas,
        "pode_estoque_insumos": pode_estoque_insumos,
        "pode_servicos": pode_servicos,
        "pode_vendas": pode_vendas,
        "pode_despesas": pode_despesas,

        "total_clientes": total_clientes,

        "total_rodas_cadastradas": total_rodas_cadastradas,
        "total_rodas_estoque": total_rodas_estoque,

        "total_insumos_cadastrados": total_insumos_cadastrados,
        "total_insumos_estoque": total_insumos_estoque,

        "servicos_em_aberto": servicos_em_aberto,

        "vendas_mes_formatado": formatar_moeda(vendas_mes),
        "servicos_mes_formatado": formatar_moeda(servicos_mes),
        "receita_mes_formatado": formatar_moeda(receita_mes),
        "despesas_mes_formatado": formatar_moeda(despesas_mes),

        "rodas_baixo_estoque": rodas_baixo_estoque,
        "insumos_baixo_estoque": insumos_baixo_estoque,

        "dashboard_charts": dashboard_charts,

        "anos_opcoes": montar_opcoes_anos(),
        "meses_opcoes": montar_opcoes_meses(),

        "ano_resumo": ano_resumo,
        "mes_resumo": mes_resumo,

        "ano_servicos": ano_servicos,
        "mes_servicos": mes_servicos,
    }

    return render(request, "dashboard/dashboard.html", context) 
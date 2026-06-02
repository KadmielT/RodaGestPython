from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from apps.estoque_rodas.models import Roda

from .forms import VendaForm
from .models import ImagemVenda, ItemVendaRoda, Venda


def parse_roda_rows(post_data):
    items = []

    item_ids = post_data.getlist('roda_id[]')
    quantidades = post_data.getlist('roda_quantidade[]')

    total_linhas = max(len(item_ids), len(quantidades))

    for i in range(total_linhas):
        item_id = item_ids[i].strip() if i < len(item_ids) and item_ids[i] else ''
        quantidade = quantidades[i].strip() if i < len(quantidades) and quantidades[i] else ''

        if not item_id and not quantidade:
            continue

        if not item_id or not quantidade:
            raise ValueError('Todas as rodas adicionadas precisam ter roda e quantidade preenchidas.')

        try:
            item_id_int = int(item_id)
            quantidade_int = int(quantidade)
        except ValueError:
            raise ValueError('A quantidade da roda deve ser um número inteiro válido.')

        if quantidade_int <= 0:
            raise ValueError('A quantidade da roda deve ser maior que zero.')

        items.append({
            'item_id': item_id_int,
            'quantidade': quantidade_int,
        })

    return items


def consolidar_itens_por_id(items):
    consolidado = {}

    for item in items:
        item_id = item['item_id']
        quantidade = item['quantidade']
        consolidado[item_id] = consolidado.get(item_id, 0) + quantidade

    return consolidado


def validar_estoque_rodas(mapa_rodas):
    erros = []

    for roda_id, quantidade in mapa_rodas.items():
        roda = Roda.objects.filter(pk=roda_id).first()

        if not roda:
            erros.append('Uma das rodas selecionadas não foi encontrada.')
            continue

        if quantidade > roda.quantidade:
            erros.append(
                f'A roda "{roda.nome}" não possui estoque suficiente. '
                f'Disponível: {roda.quantidade}. Solicitado: {quantidade}.'
            )

    return erros


def validar_ajuste_estoque_rodas(mapa_antigo, mapa_novo):
    erros = []
    todos_ids = set(mapa_antigo.keys()) | set(mapa_novo.keys())

    for roda_id in todos_ids:
        qtd_antiga = mapa_antigo.get(roda_id, 0)
        qtd_nova = mapa_novo.get(roda_id, 0)
        diferenca = qtd_nova - qtd_antiga

        if diferenca > 0:
            roda = Roda.objects.filter(pk=roda_id).first()

            if not roda:
                erros.append('Uma das rodas selecionadas não foi encontrada.')
                continue

            if diferenca > roda.quantidade:
                erros.append(
                    f'A roda "{roda.nome}" não possui estoque suficiente para a edição. '
                    f'Disponível: {roda.quantidade}. Necessário adicional: {diferenca}.'
                )

    return erros


@method_decorator(login_required, name='dispatch')
class VendaListView(ListView):
    model = Venda
    template_name = 'vendas/venda_list.html'
    context_object_name = 'vendas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Venda.objects.select_related('cliente').order_by(
            '-data_venda',
            '-data_cadastro'
        )

        q = self.request.GET.get('q', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(cliente__nome__icontains=q) |
                Q(status__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['breadcrumbs'] = [
            {'label': 'Operações'},
            {'label': 'Vendas'},
        ]
        return context


@login_required
def venda_detail(request, pk):
    venda = get_object_or_404(
        Venda.objects.select_related('cliente')
        .prefetch_related('itens_rodas__roda', 'imagens'),
        pk=pk
    )

    context = {
        'venda': venda,
        'itens_rodas': venda.itens_rodas.all(),
        'imagens': venda.imagens.all(),
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Vendas', 'url': reverse('vendas:venda_list')},
            {'label': venda.nome},
        ],
    }
    return render(request, 'vendas/venda_detail.html', context)


@login_required
def venda_create(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        imagens = request.FILES.getlist('imagens')

        try:
            rodas_data = parse_roda_rows(request.POST)
        except ValueError as e:
            messages.error(request, str(e))
        else:
            mapa_novo_rodas = consolidar_itens_por_id(rodas_data)

            if not mapa_novo_rodas:
                messages.error(request, 'Informe pelo menos uma roda para cadastrar a venda.')
            elif len(imagens) > 10:
                messages.error(request, 'Você pode enviar no máximo 10 imagens por venda.')
            elif form.is_valid():
                erros_estoque = validar_estoque_rodas(mapa_novo_rodas)

                if erros_estoque:
                    for erro in erros_estoque:
                        messages.error(request, erro)
                else:
                    with transaction.atomic():
                        venda = form.save()

                        for roda_id, quantidade in mapa_novo_rodas.items():
                            roda = Roda.objects.select_for_update().get(pk=roda_id)
                            roda.quantidade -= quantidade
                            roda.save()

                            ItemVendaRoda.objects.create(
                                venda=venda,
                                roda=roda,
                                quantidade=quantidade
                            )

                        for imagem in imagens:
                            ImagemVenda.objects.create(
                                venda=venda,
                                imagem=imagem
                            )

                    messages.success(request, f'Venda "{venda.nome}" foi criada com sucesso.')
                    return redirect('vendas:venda_list')
            else:
                messages.error(request, 'Não foi possível criar a venda. Revise os campos informados.')
    else:
        form = VendaForm()

    context = {
        'form': form,
        'titulo': 'Nova venda',
        'botao_submit': 'Salvar',
        'rodas_disponiveis': Roda.objects.order_by('nome'),
        'rodas_iniciais_json': [],
        'imagens_existentes': [],
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Vendas', 'url': reverse('vendas:venda_list')},
            {'label': 'Nova venda'},
        ],
    }
    return render(request, 'vendas/venda_form.html', context)


@login_required
def venda_update(request, pk):
    venda = get_object_or_404(
        Venda.objects.prefetch_related('itens_rodas__roda', 'imagens'),
        pk=pk
    )

    if request.method == 'POST':
        form = VendaForm(request.POST, instance=venda)
        imagens_novas = request.FILES.getlist('imagens')
        imagens_para_remover = request.POST.getlist('remover_imagens')

        try:
            rodas_data = parse_roda_rows(request.POST)
        except ValueError as e:
            messages.error(request, str(e))
        else:
            mapa_novo_rodas = consolidar_itens_por_id(rodas_data)

            if not mapa_novo_rodas:
                messages.error(request, 'Informe pelo menos uma roda para salvar a venda.')
            elif form.is_valid():
                itens_antigos_rodas = {
                    item.roda_id: item
                    for item in venda.itens_rodas.all()
                }

                mapa_antigo_rodas = {
                    item_id: item.quantidade
                    for item_id, item in itens_antigos_rodas.items()
                }

                erros_estoque = validar_ajuste_estoque_rodas(mapa_antigo_rodas, mapa_novo_rodas)

                imagens_atuais_count = venda.imagens.count()
                imagens_para_remover_count = len(imagens_para_remover)
                total_final_imagens = imagens_atuais_count - imagens_para_remover_count + len(imagens_novas)

                if total_final_imagens > 10:
                    erros_estoque.append('A venda não pode ter mais de 10 imagens no total.')

                if erros_estoque:
                    for erro in erros_estoque:
                        messages.error(request, erro)
                else:
                    with transaction.atomic():
                        venda_atualizada = form.save()

                        todos_ids_rodas = set(mapa_antigo_rodas.keys()) | set(mapa_novo_rodas.keys())

                        for roda_id in todos_ids_rodas:
                            qtd_antiga = mapa_antigo_rodas.get(roda_id, 0)
                            qtd_nova = mapa_novo_rodas.get(roda_id, 0)
                            diferenca = qtd_nova - qtd_antiga

                            if diferenca != 0:
                                roda = Roda.objects.select_for_update().get(pk=roda_id)

                                if diferenca > 0:
                                    roda.quantidade -= diferenca
                                else:
                                    roda.quantidade += abs(diferenca)

                                roda.save()

                        ids_antigos_rodas = set(itens_antigos_rodas.keys())
                        ids_novos_rodas = set(mapa_novo_rodas.keys())

                        ids_para_remover_rodas = ids_antigos_rodas - ids_novos_rodas
                        ids_para_criar_rodas = ids_novos_rodas - ids_antigos_rodas
                        ids_para_atualizar_rodas = ids_antigos_rodas & ids_novos_rodas

                        for roda_id in ids_para_remover_rodas:
                            itens_antigos_rodas[roda_id].delete()

                        for roda_id in ids_para_atualizar_rodas:
                            item_existente = itens_antigos_rodas[roda_id]
                            item_existente.quantidade = mapa_novo_rodas[roda_id]
                            item_existente.save()

                        for roda_id in ids_para_criar_rodas:
                            ItemVendaRoda.objects.create(
                                venda=venda_atualizada,
                                roda_id=roda_id,
                                quantidade=mapa_novo_rodas[roda_id]
                            )

                        if imagens_para_remover:
                            imagens_remover_qs = venda_atualizada.imagens.filter(id__in=imagens_para_remover)

                            for imagem in imagens_remover_qs:
                                if imagem.imagem:
                                    imagem.imagem.delete(save=False)
                                imagem.delete()

                        for imagem in imagens_novas:
                            ImagemVenda.objects.create(
                                venda=venda_atualizada,
                                imagem=imagem
                            )

                    messages.success(request, f'Venda "{venda_atualizada.nome}" foi atualizada com sucesso.')
                    return redirect('vendas:venda_list')
            else:
                messages.error(request, f'Não foi possível salvar as alterações da venda "{venda.nome}".')
    else:
        form = VendaForm(instance=venda)

    rodas_iniciais = [
        {'id': item.roda_id, 'quantidade': item.quantidade}
        for item in venda.itens_rodas.all()
    ]

    context = {
        'form': form,
        'venda': venda,
        'titulo': 'Editar venda',
        'botao_submit': 'Salvar alterações',
        'modo_edicao': True,
        'rodas_disponiveis': Roda.objects.order_by('nome'),
        'rodas_iniciais_json': rodas_iniciais,
        'imagens_existentes': venda.imagens.all(),
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Vendas', 'url': reverse('vendas:venda_list')},
            {'label': venda.nome},
            {'label': 'Editar'},
        ],
    }
    return render(request, 'vendas/venda_form.html', context)


@login_required
def venda_delete(request, pk):
    venda = get_object_or_404(
        Venda.objects.prefetch_related('itens_rodas__roda'),
        pk=pk
    )

    if request.method == 'POST':
        nome_venda = venda.nome

        with transaction.atomic():
            for item in venda.itens_rodas.all():
                roda = Roda.objects.select_for_update().get(pk=item.roda_id)
                roda.quantidade += item.quantidade
                roda.save()

            venda.delete()

        messages.success(request, f'Venda "{nome_venda}" foi excluída com sucesso.')
        return redirect('vendas:venda_list')

    return redirect('vendas:venda_list')
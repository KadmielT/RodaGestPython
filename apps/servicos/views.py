from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from apps.estoque_insumos.models import Insumo
from apps.estoque_rodas.models import Roda

from .forms import ServicoForm
from .models import ImagemServico, ItemServicoInsumo, ItemServicoRoda, Servico


def parse_item_rows(post_data, item_type):
    items = []

    if item_type == 'roda':
        item_ids = post_data.getlist('roda_id[]')
        quantidades = post_data.getlist('roda_quantidade[]')
    else:
        item_ids = post_data.getlist('insumo_id[]')
        quantidades = post_data.getlist('insumo_quantidade[]')

    total_linhas = max(len(item_ids), len(quantidades))

    for i in range(total_linhas):
        item_id = item_ids[i].strip() if i < len(item_ids) and item_ids[i] else ''
        quantidade = quantidades[i].strip() if i < len(quantidades) and quantidades[i] else ''

        if not item_id and not quantidade:
            continue

        if not item_id or not quantidade:
            raise ValueError('Todos os itens adicionados precisam ter item e quantidade preenchidos.')

        try:
            quantidade_int = int(quantidade)
        except ValueError:
            raise ValueError('A quantidade deve ser um número inteiro válido.')

        if quantidade_int <= 0:
            raise ValueError('A quantidade deve ser maior que zero.')

        items.append({
            'item_id': int(item_id),
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


def validar_estoque_rodas(rodas_data):
    erros = []

    for item in rodas_data:
        roda = Roda.objects.filter(pk=item['item_id']).first()

        if not roda:
            erros.append('Uma das rodas selecionadas não foi encontrada.')
            continue

        if item['quantidade'] > roda.quantidade:
            erros.append(
                f'A roda "{roda.nome}" não possui estoque suficiente. '
                f'Disponível: {roda.quantidade}. Solicitado: {item["quantidade"]}.'
            )

    return erros


def validar_estoque_insumos(insumos_data):
    erros = []

    for item in insumos_data:
        insumo = Insumo.objects.filter(pk=item['item_id']).first()

        if not insumo:
            erros.append('Um dos insumos selecionados não foi encontrado.')
            continue

        if item['quantidade'] > insumo.quantidade:
            erros.append(
                f'O insumo "{insumo.nome}" não possui estoque suficiente. '
                f'Disponível: {insumo.quantidade}. Solicitado: {item["quantidade"]}.'
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


def validar_ajuste_estoque_insumos(mapa_antigo, mapa_novo):
    erros = []
    todos_ids = set(mapa_antigo.keys()) | set(mapa_novo.keys())

    for insumo_id in todos_ids:
        qtd_antiga = mapa_antigo.get(insumo_id, 0)
        qtd_nova = mapa_novo.get(insumo_id, 0)
        diferenca = qtd_nova - qtd_antiga

        if diferenca > 0:
            insumo = Insumo.objects.filter(pk=insumo_id).first()

            if not insumo:
                erros.append('Um dos insumos selecionados não foi encontrado.')
                continue

            if diferenca > insumo.quantidade:
                erros.append(
                    f'O insumo "{insumo.nome}" não possui estoque suficiente para a edição. '
                    f'Disponível: {insumo.quantidade}. Necessário adicional: {diferenca}.'
                )

    return erros


@method_decorator(login_required, name='dispatch')
class ServicoListView(ListView):
    model = Servico
    template_name = 'servicos/servico_list.html'
    context_object_name = 'servicos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Servico.objects.select_related('cliente').order_by(
            '-data_servico',
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
            {'label': 'Serviços'},
        ]
        return context


@login_required
def servico_detail(request, pk):
    servico = get_object_or_404(
        Servico.objects.select_related('cliente')
        .prefetch_related('itens_rodas__roda', 'itens_insumos__insumo', 'imagens'),
        pk=pk
    )

    context = {
        'servico': servico,
        'itens_rodas': servico.itens_rodas.all(),
        'itens_insumos': servico.itens_insumos.all(),
        'imagens': servico.imagens.all(),
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Serviços', 'url': reverse('servicos:servico_list')},
            {'label': servico.nome},
        ],
    }
    return render(request, 'servicos/servico_detail.html', context)


@login_required
def servico_create(request):
    if request.method == 'POST':
        form = ServicoForm(request.POST)
        imagens = request.FILES.getlist('imagens')

        try:
            rodas_data = parse_item_rows(request.POST, 'roda')
            insumos_data = parse_item_rows(request.POST, 'insumo')
        except ValueError as e:
            messages.error(request, str(e))
        else:
            if len(imagens) > 10:
                messages.error(request, 'Você pode enviar no máximo 10 imagens por serviço.')
            elif form.is_valid():
                erros_estoque = []
                erros_estoque.extend(validar_estoque_rodas(rodas_data))
                erros_estoque.extend(validar_estoque_insumos(insumos_data))

                if erros_estoque:
                    for erro in erros_estoque:
                        messages.error(request, erro)
                else:
                    with transaction.atomic():
                        servico = form.save()

                        mapa_novo_rodas = consolidar_itens_por_id(rodas_data)
                        mapa_novo_insumos = consolidar_itens_por_id(insumos_data)

                        for roda_id, quantidade in mapa_novo_rodas.items():
                            roda = Roda.objects.select_for_update().get(pk=roda_id)
                            roda.quantidade -= quantidade
                            roda.save()

                            ItemServicoRoda.objects.create(
                                servico=servico,
                                roda=roda,
                                quantidade=quantidade
                            )

                        for insumo_id, quantidade in mapa_novo_insumos.items():
                            insumo = Insumo.objects.select_for_update().get(pk=insumo_id)
                            insumo.quantidade -= quantidade
                            insumo.save()

                            ItemServicoInsumo.objects.create(
                                servico=servico,
                                insumo=insumo,
                                quantidade=quantidade
                            )

                        for imagem in imagens:
                            ImagemServico.objects.create(
                                servico=servico,
                                imagem=imagem
                            )

                    messages.success(request, f'Serviço "{servico.nome}" foi criado com sucesso.')
                    return redirect('servicos:servico_list')
            else:
                messages.error(request, 'Não foi possível criar o serviço. Revise os campos informados.')
    else:
        form = ServicoForm()

    context = {
        'form': form,
        'titulo': 'Novo serviço',
        'botao_submit': 'Salvar',
        'rodas_disponiveis': Roda.objects.order_by('nome'),
        'insumos_disponiveis': Insumo.objects.order_by('nome'),
        'rodas_iniciais_json': [],
        'insumos_iniciais_json': [],
        'imagens_existentes': [],
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Serviços', 'url': reverse('servicos:servico_list')},
            {'label': 'Novo serviço'},
        ],
    }
    return render(request, 'servicos/servico_form.html', context)


@login_required
def servico_update(request, pk):
    servico = get_object_or_404(
        Servico.objects.prefetch_related('itens_rodas__roda', 'itens_insumos__insumo', 'imagens'),
        pk=pk
    )

    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico)
        imagens_novas = request.FILES.getlist('imagens')
        imagens_para_remover = request.POST.getlist('remover_imagens')

        try:
            rodas_data = parse_item_rows(request.POST, 'roda')
            insumos_data = parse_item_rows(request.POST, 'insumo')
        except ValueError as e:
            messages.error(request, str(e))
        else:
            if form.is_valid():
                itens_antigos_rodas = {
                    item.roda_id: item
                    for item in servico.itens_rodas.all()
                }
                itens_antigos_insumos = {
                    item.insumo_id: item
                    for item in servico.itens_insumos.all()
                }

                mapa_antigo_rodas = {
                    item_id: item.quantidade
                    for item_id, item in itens_antigos_rodas.items()
                }
                mapa_antigo_insumos = {
                    item_id: item.quantidade
                    for item_id, item in itens_antigos_insumos.items()
                }

                mapa_novo_rodas = consolidar_itens_por_id(rodas_data)
                mapa_novo_insumos = consolidar_itens_por_id(insumos_data)

                erros_estoque = []
                erros_estoque.extend(validar_ajuste_estoque_rodas(mapa_antigo_rodas, mapa_novo_rodas))
                erros_estoque.extend(validar_ajuste_estoque_insumos(mapa_antigo_insumos, mapa_novo_insumos))

                imagens_atuais_count = servico.imagens.count()
                imagens_para_remover_count = len(imagens_para_remover)
                total_final_imagens = imagens_atuais_count - imagens_para_remover_count + len(imagens_novas)

                if total_final_imagens > 10:
                    erros_estoque.append('O serviço não pode ter mais de 10 imagens no total.')

                if erros_estoque:
                    for erro in erros_estoque:
                        messages.error(request, erro)
                else:
                    with transaction.atomic():
                        servico_atualizado = form.save()

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

                        todos_ids_insumos = set(mapa_antigo_insumos.keys()) | set(mapa_novo_insumos.keys())
                        for insumo_id in todos_ids_insumos:
                            qtd_antiga = mapa_antigo_insumos.get(insumo_id, 0)
                            qtd_nova = mapa_novo_insumos.get(insumo_id, 0)
                            diferenca = qtd_nova - qtd_antiga

                            if diferenca != 0:
                                insumo = Insumo.objects.select_for_update().get(pk=insumo_id)

                                if diferenca > 0:
                                    insumo.quantidade -= diferenca
                                else:
                                    insumo.quantidade += abs(diferenca)

                                insumo.save()

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
                            ItemServicoRoda.objects.create(
                                servico=servico_atualizado,
                                roda_id=roda_id,
                                quantidade=mapa_novo_rodas[roda_id]
                            )

                        ids_antigos_insumos = set(itens_antigos_insumos.keys())
                        ids_novos_insumos = set(mapa_novo_insumos.keys())

                        ids_para_remover_insumos = ids_antigos_insumos - ids_novos_insumos
                        ids_para_criar_insumos = ids_novos_insumos - ids_antigos_insumos
                        ids_para_atualizar_insumos = ids_antigos_insumos & ids_novos_insumos

                        for insumo_id in ids_para_remover_insumos:
                            itens_antigos_insumos[insumo_id].delete()

                        for insumo_id in ids_para_atualizar_insumos:
                            item_existente = itens_antigos_insumos[insumo_id]
                            item_existente.quantidade = mapa_novo_insumos[insumo_id]
                            item_existente.save()

                        for insumo_id in ids_para_criar_insumos:
                            ItemServicoInsumo.objects.create(
                                servico=servico_atualizado,
                                insumo_id=insumo_id,
                                quantidade=mapa_novo_insumos[insumo_id]
                            )

                        if imagens_para_remover:
                            imagens_remover_qs = servico_atualizado.imagens.filter(id__in=imagens_para_remover)
                            for imagem in imagens_remover_qs:
                                if imagem.imagem:
                                    imagem.imagem.delete(save=False)
                                imagem.delete()

                        for imagem in imagens_novas:
                            ImagemServico.objects.create(
                                servico=servico_atualizado,
                                imagem=imagem
                            )

                    messages.success(request, f'Serviço "{servico_atualizado.nome}" foi atualizado com sucesso.')
                    return redirect('servicos:servico_list')
            else:
                messages.error(request, f'Não foi possível salvar as alterações do serviço "{servico.nome}".')
    else:
        form = ServicoForm(instance=servico)

    rodas_iniciais = [
        {'id': item.roda_id, 'quantidade': item.quantidade}
        for item in servico.itens_rodas.all()
    ]
    insumos_iniciais = [
        {'id': item.insumo_id, 'quantidade': item.quantidade}
        for item in servico.itens_insumos.all()
    ]

    context = {
        'form': form,
        'servico': servico,
        'titulo': 'Editar serviço',
        'botao_submit': 'Salvar alterações',
        'modo_edicao': True,
        'rodas_disponiveis': Roda.objects.order_by('nome'),
        'insumos_disponiveis': Insumo.objects.order_by('nome'),
        'rodas_iniciais_json': rodas_iniciais,
        'insumos_iniciais_json': insumos_iniciais,
        'imagens_existentes': servico.imagens.all(),
        'breadcrumbs': [
            {'label': 'Operações'},
            {'label': 'Serviços', 'url': reverse('servicos:servico_list')},
            {'label': servico.nome},
            {'label': 'Editar'},
        ],
    }
    return render(request, 'servicos/servico_form.html', context)


@login_required
def servico_delete(request, pk):
    servico = get_object_or_404(Servico, pk=pk)

    if request.method == 'POST':
        servico_id = servico.pk
        nome_servico = servico.nome
        arquivos_imagens = []

        try:
            with transaction.atomic():
                itens_rodas = list(
                    ItemServicoRoda.objects
                    .filter(servico_id=servico_id)
                    .values('roda_id', 'quantidade')
                )

                itens_insumos = list(
                    ItemServicoInsumo.objects
                    .filter(servico_id=servico_id)
                    .values('insumo_id', 'quantidade')
                )

                imagens = list(
                    ImagemServico.objects
                    .filter(servico_id=servico_id)
                )

                for imagem in imagens:
                    if imagem.imagem:
                        arquivos_imagens.append(imagem.imagem)

                for item in itens_rodas:
                    Roda.objects.filter(pk=item['roda_id']).update(
                        quantidade=F('quantidade') + item['quantidade']
                    )

                for item in itens_insumos:
                    Insumo.objects.filter(pk=item['insumo_id']).update(
                        quantidade=F('quantidade') + item['quantidade']
                    )

                ItemServicoRoda.objects.filter(servico_id=servico_id).delete()
                ItemServicoInsumo.objects.filter(servico_id=servico_id).delete()
                ImagemServico.objects.filter(servico_id=servico_id).delete()

                Servico.objects.filter(pk=servico_id).delete()

            for arquivo in arquivos_imagens:
                arquivo.delete(save=False)

            messages.success(
                request,
                f'Serviço "{nome_servico}" foi excluído com sucesso. As rodas e os insumos foram devolvidos ao estoque.'
            )

        except IntegrityError as erro:
            print("ERRO AO EXCLUIR SERVIÇO:", erro)
            print("SERVIÇO ID:", servico_id)

            for rel in Servico._meta.related_objects:
                model = rel.related_model
                field_name = rel.field.name

                try:
                    total = model.objects.filter(**{f"{field_name}_id": servico_id}).count()
                except Exception:
                    total = model.objects.filter(**{field_name: servico_id}).count()

                print(
                    "VÍNCULO ENCONTRADO:",
                    model._meta.label,
                    "| campo:",
                    field_name,
                    "| registros:",
                    total,
                    "| on_delete:",
                    rel.on_delete,
                )

            messages.error(
                request,
                f'Não foi possível excluir o serviço "{nome_servico}". Ainda existe algum registro vinculado no banco.'
            )

        return redirect('servicos:servico_list')

    return redirect('servicos:servico_list')
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .forms import InsumoForm, MovimentacaoInsumoForm
from .models import Insumo, MovimentacaoInsumo


@method_decorator(login_required, name='dispatch')
class InsumoListView(ListView):
    model = Insumo
    template_name = 'estoque_insumos/insumo_list.html'
    context_object_name = 'insumos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Insumo.objects.all().order_by('nome')
        q = self.request.GET.get('q', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(codigo__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['breadcrumbs'] = [
            {'label': 'Cadastro'},
            {'label': 'Estoque de insumos'},
        ]
        return context


@login_required
def insumo_create(request):
    if request.method == 'POST':
        form = InsumoForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                insumo = form.save(commit=False)
                insumo.quantidade_inicial = form.cleaned_data['quantidade']
                insumo.save()

            messages.success(request, f'Insumo "{insumo.nome}" foi criado com sucesso.')
            return redirect('estoque_insumos:insumo_list')

        messages.error(request, 'Não foi possível criar o insumo. Revise os campos informados.')
    else:
        form = InsumoForm()

    context = {
        'form': form,
        'titulo': 'Novo insumo',
        'botao_submit': 'Salvar',
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de insumos', 'url': reverse('estoque_insumos:insumo_list')},
            {'label': 'Novo insumo'},
        ],
    }
    return render(request, 'estoque_insumos/insumo_form.html', context)


@login_required
def insumo_detail(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    movimentacoes = insumo.movimentacoes.all().order_by('-data_cadastro')

    context = {
        'insumo': insumo,
        'movimentacoes': movimentacoes,
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de insumos', 'url': reverse('estoque_insumos:insumo_list')},
            {'label': insumo.nome},
        ],
    }
    return render(request, 'estoque_insumos/insumo_detail.html', context)


@login_required
def insumo_update(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    if request.method == 'POST':
        form = InsumoForm(request.POST, instance=insumo)

        if form.is_valid():
            insumo_atualizado = form.save(commit=False)
            insumo_atualizado.quantidade = insumo.quantidade
            insumo_atualizado.quantidade_inicial = insumo.quantidade_inicial
            insumo_atualizado.save()

            messages.success(request, f'Insumo "{insumo_atualizado.nome}" foi atualizado com sucesso.')
            return redirect('estoque_insumos:insumo_list')

        messages.error(request, f'Não foi possível salvar as alterações do insumo "{insumo.nome}".')
    else:
        form = InsumoForm(instance=insumo)

    context = {
        'form': form,
        'titulo': 'Editar insumo',
        'botao_submit': 'Salvar alterações',
        'insumo': insumo,
        'modo_edicao': True,
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de insumos', 'url': reverse('estoque_insumos:insumo_list')},
            {'label': insumo.nome},
            {'label': 'Editar'},
        ],
    }
    return render(request, 'estoque_insumos/insumo_form.html', context)


@login_required
def movimentar_insumo(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    if request.method == 'POST':
        form = MovimentacaoInsumoForm(request.POST)

        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.insumo = insumo

            with transaction.atomic():
                if movimentacao.tipo_movimentacao == MovimentacaoInsumo.TipoMovimentacaoChoices.ENTRADA:
                    insumo.quantidade += movimentacao.quantidade
                else:
                    if movimentacao.quantidade > insumo.quantidade:
                        form.add_error('quantidade', 'A saída não pode ser maior que a quantidade disponível em estoque.')
                    else:
                        insumo.quantidade -= movimentacao.quantidade

                if not form.errors:
                    movimentacao.full_clean()
                    insumo.save()
                    movimentacao.save()
                    messages.success(
                        request,
                        f'Movimentação do insumo "{insumo.nome}" registrada com sucesso.'
                    )
                    return redirect('estoque_insumos:insumo_list')

        messages.error(
            request,
            f'Não foi possível registrar a movimentação do insumo "{insumo.nome}".'
        )
    else:
        form = MovimentacaoInsumoForm()

    context = {
        'form': form,
        'insumo': insumo,
        'titulo': 'Movimentar estoque',
        'botao_submit': 'Registrar movimentação',
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de insumos', 'url': reverse('estoque_insumos:insumo_list')},
            {'label': insumo.nome},
            {'label': 'Movimentar estoque'},
        ],
    }
    return render(request, 'estoque_insumos/movimentacao_insumo_form.html', context)


@login_required
def insumo_delete(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)

    if request.method == 'POST':
        nome_insumo = insumo.nome
        insumo.delete()
        messages.success(request, f'Insumo "{nome_insumo}" foi excluído com sucesso.')
        return redirect('estoque_insumos:insumo_list')

    return redirect('estoque_insumos:insumo_list')
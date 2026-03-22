from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .forms import MovimentacaoRodaForm, RodaForm
from .models import MovimentacaoRoda, Roda


@method_decorator(login_required, name='dispatch')
class RodaListView(ListView):
    model = Roda
    template_name = 'estoque_rodas/roda_list.html'
    context_object_name = 'rodas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Roda.objects.all().order_by('nome')
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
            {'label': 'Estoque de rodas'},
        ]
        return context


@login_required
def roda_create(request):
    if request.method == 'POST':
        form = RodaForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                roda = form.save(commit=False)
                roda.quantidade_inicial = form.cleaned_data['quantidade']
                roda.save()

            messages.success(request, f'Roda "{roda.nome}" foi criada com sucesso.')
            return redirect('estoque_rodas:roda_list')

        messages.error(request, 'Não foi possível criar a roda. Revise os campos informados.')
    else:
        form = RodaForm()

    context = {
        'form': form,
        'titulo': 'Nova roda',
        'botao_submit': 'Salvar',
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de rodas', 'url': reverse('estoque_rodas:roda_list')},
            {'label': 'Nova roda'},
        ],
    }
    return render(request, 'estoque_rodas/roda_form.html', context)


@login_required
def roda_detail(request, pk):
    roda = get_object_or_404(Roda, pk=pk)
    movimentacoes = roda.movimentacoes.all().order_by('-data_cadastro')

    context = {
        'roda': roda,
        'movimentacoes': movimentacoes,
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de rodas', 'url': reverse('estoque_rodas:roda_list')},
            {'label': roda.nome},
        ],
    }
    return render(request, 'estoque_rodas/roda_detail.html', context)


@login_required
def roda_update(request, pk):
    roda = get_object_or_404(Roda, pk=pk)

    if request.method == 'POST':
        form = RodaForm(request.POST, instance=roda)

        if form.is_valid():
            roda_atualizada = form.save(commit=False)
            roda_atualizada.quantidade = roda.quantidade
            roda_atualizada.quantidade_inicial = roda.quantidade_inicial
            roda_atualizada.save()

            messages.success(request, f'Roda "{roda_atualizada.nome}" foi atualizada com sucesso.')
            return redirect('estoque_rodas:roda_list')

        messages.error(request, f'Não foi possível salvar as alterações da roda "{roda.nome}".')
    else:
        form = RodaForm(instance=roda)

    context = {
        'form': form,
        'titulo': 'Editar roda',
        'botao_submit': 'Salvar alterações',
        'roda': roda,
        'modo_edicao': True,
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de rodas', 'url': reverse('estoque_rodas:roda_list')},
            {'label': roda.nome},
            {'label': 'Editar'},
        ],
    }
    return render(request, 'estoque_rodas/roda_form.html', context)


@login_required
def movimentar_roda(request, pk):
    roda = get_object_or_404(Roda, pk=pk)

    if request.method == 'POST':
        form = MovimentacaoRodaForm(request.POST)

        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.roda = roda

            with transaction.atomic():
                if movimentacao.tipo_movimentacao == MovimentacaoRoda.TipoMovimentacaoChoices.ENTRADA:
                    roda.quantidade += movimentacao.quantidade
                else:
                    if movimentacao.quantidade > roda.quantidade:
                        form.add_error('quantidade', 'A saída não pode ser maior que a quantidade disponível em estoque.')
                    else:
                        roda.quantidade -= movimentacao.quantidade

                if not form.errors:
                    movimentacao.full_clean()
                    roda.save()
                    movimentacao.save()
                    messages.success(
                        request,
                        f'Movimentação da roda "{roda.nome}" registrada com sucesso.'
                    )
                    return redirect('estoque_rodas:roda_list')

        messages.error(
            request,
            f'Não foi possível registrar a movimentação da roda "{roda.nome}".'
        )
    else:
        form = MovimentacaoRodaForm()

    context = {
        'form': form,
        'roda': roda,
        'titulo': 'Movimentar estoque',
        'botao_submit': 'Registrar movimentação',
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de rodas', 'url': reverse('estoque_rodas:roda_list')},
            {'label': roda.nome},
            {'label': 'Movimentar estoque'},
        ],
    }
    return render(request, 'estoque_rodas/movimentacao_form.html', context)


@login_required
def roda_delete(request, pk):
    roda = get_object_or_404(Roda, pk=pk)

    if request.method == 'POST':
        nome_roda = roda.nome
        roda.delete()
        messages.success(request, f'Roda "{nome_roda}" foi excluída com sucesso.')
        return redirect('estoque_rodas:roda_list')

    return redirect('estoque_rodas:roda_list')
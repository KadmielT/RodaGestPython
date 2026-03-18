from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

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
                Q(nome__icontains=q) | Q(codigo__icontains=q)
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
            form.save()
            messages.success(request, 'Roda cadastrada com sucesso.')
            return redirect('estoque_rodas:roda_list')
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
            form.save()
            messages.success(request, 'Roda atualizada com sucesso.')
            return redirect('estoque_rodas:roda_list')
    else:
        form = RodaForm(instance=roda)

    context = {
        'form': form,
        'titulo': 'Editar roda',
        'botao_submit': 'Salvar alterações',
        'roda': roda,
        'breadcrumbs': [
            {'label': 'Cadastro'},
            {'label': 'Estoque de rodas', 'url': reverse('estoque_rodas:roda_list')},
            {'label': roda.nome, 'url': reverse('estoque_rodas:roda_detail', kwargs={'pk': roda.pk})},
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
                    messages.success(request, 'Movimentação registrada com sucesso.')
                    return redirect('estoque_rodas:roda_list')
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
            {'label': roda.nome, 'url': reverse('estoque_rodas:roda_detail', kwargs={'pk': roda.pk})},
            {'label': 'Movimentar estoque'},
        ],
    }
    return render(request, 'estoque_rodas/movimentacao_form.html', context)
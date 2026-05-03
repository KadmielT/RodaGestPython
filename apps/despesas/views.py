from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .forms import DespesaForm
from .models import ArquivoDespesa, Despesa


def salvar_arquivos_despesa(despesa, arquivos):
    for arquivo in arquivos:
        ArquivoDespesa.objects.create(
            despesa=despesa,
            arquivo=arquivo,
            nome_original=arquivo.name
        )


def remover_arquivos_despesa(despesa, arquivos_ids):
    arquivos = ArquivoDespesa.objects.filter(
        despesa=despesa,
        pk__in=arquivos_ids
    )

    for arquivo in arquivos:
        if arquivo.arquivo:
            arquivo.arquivo.delete(save=False)

        arquivo.delete()


def remover_todos_arquivos_despesa(despesa):
    arquivos = despesa.arquivos.all()

    for arquivo in arquivos:
        if arquivo.arquivo:
            arquivo.arquivo.delete(save=False)


@method_decorator(login_required, name='dispatch')
class DespesaListView(ListView):
    model = Despesa
    template_name = 'despesas/despesa_list.html'
    context_object_name = 'despesas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Despesa.objects.all().order_by('-data_cadastro')
        q = self.request.GET.get('q', '').strip()

        if q:
            queryset = queryset.filter(
                Q(descricao__icontains=q) |
                Q(categoria__icontains=q) |
                Q(status__icontains=q) |
                Q(forma_pagamento__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['q'] = self.request.GET.get('q', '')
        context['breadcrumbs'] = [
            {'label': 'Financeiro'},
            {'label': 'Despesas'},
        ]

        return context


@login_required
def despesa_create(request):
    if request.method == 'POST':
        form = DespesaForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                despesa = form.save()
                salvar_arquivos_despesa(
                    despesa,
                    request.FILES.getlist('arquivos')
                )

            messages.success(
                request,
                f'Despesa "{despesa.descricao}" foi cadastrada com sucesso.'
            )
            return redirect('despesas:despesa_list')

        messages.error(
            request,
            'Não foi possível cadastrar a despesa. Revise os campos informados.'
        )
    else:
        form = DespesaForm()

    context = {
        'form': form,
        'titulo': 'Nova despesa',
        'botao_submit': 'Salvar',
        'arquivos': [],
        'breadcrumbs': [
            {'label': 'Financeiro'},
            {'label': 'Despesas', 'url': reverse('despesas:despesa_list')},
            {'label': 'Nova despesa'},
        ],
    }

    return render(request, 'despesas/despesa_form.html', context)


@login_required
def despesa_detail(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)
    arquivos = despesa.arquivos.all()

    context = {
        'despesa': despesa,
        'arquivos': arquivos,
        'breadcrumbs': [
            {'label': 'Financeiro'},
            {'label': 'Despesas', 'url': reverse('despesas:despesa_list')},
            {'label': despesa.descricao},
        ],
    }

    return render(request, 'despesas/despesa_detail.html', context)


@login_required
def despesa_update(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)

    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa)

        if form.is_valid():
            with transaction.atomic():
                despesa_atualizada = form.save()

                arquivos_para_remover = request.POST.getlist('remover_arquivos')

                if arquivos_para_remover:
                    remover_arquivos_despesa(
                        despesa_atualizada,
                        arquivos_para_remover
                    )

                salvar_arquivos_despesa(
                    despesa_atualizada,
                    request.FILES.getlist('arquivos')
                )

            messages.success(
                request,
                f'Despesa "{despesa_atualizada.descricao}" foi atualizada com sucesso.'
            )
            return redirect('despesas:despesa_list')

        messages.error(
            request,
            f'Não foi possível salvar as alterações da despesa "{despesa.descricao}".'
        )
    else:
        form = DespesaForm(instance=despesa)

    context = {
        'form': form,
        'despesa': despesa,
        'arquivos': despesa.arquivos.all(),
        'titulo': 'Editar despesa',
        'botao_submit': 'Salvar alterações',
        'breadcrumbs': [
            {'label': 'Financeiro'},
            {'label': 'Despesas', 'url': reverse('despesas:despesa_list')},
            {'label': despesa.descricao},
            {'label': 'Editar'},
        ],
    }

    return render(request, 'despesas/despesa_form.html', context)


@login_required
def despesa_delete(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)

    if request.method == 'POST':
        descricao_despesa = despesa.descricao

        remover_todos_arquivos_despesa(despesa)
        despesa.delete()

        messages.success(
            request,
            f'Despesa "{descricao_despesa}" foi excluída com sucesso.'
        )
        return redirect('despesas:despesa_list')

    return redirect('despesas:despesa_list')
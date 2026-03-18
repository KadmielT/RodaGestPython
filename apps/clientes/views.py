from django.views.generic import ListView
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .models import Cliente, Endereco
from .forms import ClienteForm, EnderecoForm


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Cliente.objects.order_by("-data_cadastro")
        busca = self.request.GET.get("q", "").strip()

        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(documento__icontains=busca) |
                Q(email__icontains=busca)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["breadcrumbs"] = [
            {"label": "Cadastro"},
            {"label": "Clientes"},
        ]
        return context


@login_required
def cliente_create(request):
    if request.method == "POST":
        cliente_form = ClienteForm(request.POST)
        endereco_form = EnderecoForm(request.POST)

        if cliente_form.is_valid() and endereco_form.is_valid():
            cliente = cliente_form.save()

            endereco = endereco_form.save(commit=False)
            endereco.cliente = cliente
            endereco.save()

            messages.success(request, "Cliente criado com sucesso!")
            return redirect("clientes:cliente_list")
    else:
        cliente_form = ClienteForm()
        endereco_form = EnderecoForm()

    context = {
        "cliente_form": cliente_form,
        "endereco_form": endereco_form,
        "breadcrumbs": [
            {"label": "Cadastro"},
            {"label": "Clientes", "url": reverse("clientes:cliente_list")},
            {"label": "Novo cliente"},
        ]
    }

    return render(request, "clientes/cliente_form.html", context)


@login_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    endereco = getattr(cliente, "endereco", None)

    context = {
        "cliente": cliente,
        "endereco": endereco,
        "breadcrumbs": [
            {"label": "Cadastro"},
            {"label": "Clientes", "url": reverse("clientes:cliente_list")},
            {"label": cliente.nome},
        ],
    }
    return render(request, "clientes/cliente_detail.html", context)


@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    endereco = getattr(cliente, "endereco", None)

    if request.method == "POST":
        cliente_form = ClienteForm(request.POST, instance=cliente)
        endereco_form = EnderecoForm(request.POST, instance=endereco)

        if cliente_form.is_valid() and endereco_form.is_valid():
            cliente = cliente_form.save()
            endereco = endereco_form.save(commit=False)
            endereco.cliente = cliente
            endereco.save()

            messages.success(request, "Cliente atualizado com sucesso!")
            return redirect("clientes:cliente_list")
    else:
        cliente_form = ClienteForm(instance=cliente)
        endereco_form = EnderecoForm(instance=endereco)

    context = {
        "cliente_form": cliente_form,
        "endereco_form": endereco_form,
        "modo_edicao": True,
        "cliente": cliente,
        "breadcrumbs": [
            {"label": "Cadastro"},
            {"label": "Clientes", "url": reverse("clientes:cliente_list")},
            {"label": cliente.nome, "url": reverse("clientes:cliente_detail", kwargs={"pk": cliente.pk})},
            {"label": "Editar"},
        ],
    }
    return render(request, "clientes/cliente_form.html", context)


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == "POST":
        cliente.delete()
        messages.success(request, "Cliente excluído com sucesso!")
        return redirect("clientes:cliente_list")

    return redirect("clientes:cliente_list")
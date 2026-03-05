from django.views.generic import ListView
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Cliente
from .forms import ClienteForm


class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        # Aqui a gente pega todos os clientes ordenados do mais novo pro mais antigo
        queryset = Cliente.objects.order_by("-data_cadastro")

        # Pega o valor digitado no input de busca (?q=...)
        busca = self.request.GET.get("q", "").strip()

        # Se tiver algo digitado, aplica filtro (nome, documento ou email)
        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(documento__icontains=busca) |
                Q(email__icontains=busca)
            )

        return queryset

    def get_context_data(self, **kwargs):
        # Contexto padrão do ListView (clientes, page_obj, is_paginated, etc.)
        context = super().get_context_data(**kwargs)

        # Mantém o valor da busca no input após pesquisar
        context["q"] = self.request.GET.get("q", "")

        # ✅ Aqui é o breadcrumb que o template "partials/breadcrumbs.html" espera
        context["breadcrumbs"] = [
            {"label": "Registros", "url": "#"},
            {"label": "Clientes", "url": None},
        ]

        return context


def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Cliente criado com sucesso!")
            return redirect("cliente_list")
    else:
        form = ClienteForm()

    return render(request, "clientes/cliente_form.html", {"form": form})
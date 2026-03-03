from django.views.generic import ListView
from django.db.models import Q
from .models import Cliente


class ClienteListView(ListView):
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
        return context
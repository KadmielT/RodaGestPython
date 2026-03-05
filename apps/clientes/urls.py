from django.urls import path
from .views import ClienteListView, cliente_create

urlpatterns = [
    path("", ClienteListView.as_view(), name="cliente_list"),
    path("clientes/novo/", cliente_create, name="cliente_create"),
]
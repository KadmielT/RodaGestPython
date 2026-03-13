from django.urls import path
from .views import (
    ClienteListView,
    cliente_create,
    cliente_detail,
    cliente_update,
    cliente_delete,
)

app_name = "clientes"

urlpatterns = [
    path("", ClienteListView.as_view(), name="cliente_list"),
    path("novo/", cliente_create, name="cliente_create"),
    path("<int:pk>/", cliente_detail, name="cliente_detail"),
    path("<int:pk>/editar/", cliente_update, name="cliente_update"),
    path("<int:pk>/excluir/", cliente_delete, name="cliente_delete"),
]
from django.urls import path

from .views import (
    InsumoListView,
    insumo_create,
    insumo_delete,
    insumo_detail,
    insumo_update,
    movimentar_insumo,
)

app_name = 'estoque_insumos'

urlpatterns = [
    path('', InsumoListView.as_view(), name='insumo_list'),
    path('novo/', insumo_create, name='insumo_create'),
    path('<int:pk>/', insumo_detail, name='insumo_detail'),
    path('<int:pk>/editar/', insumo_update, name='insumo_update'),
    path('<int:pk>/movimentar/', movimentar_insumo, name='movimentar_insumo'),
    path('<int:pk>/excluir/', insumo_delete, name='insumo_delete'),
]
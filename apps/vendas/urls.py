from django.urls import path

from .views import (
    VendaListView,
    venda_create,
    venda_delete,
    venda_detail,
    venda_update,
)

app_name = 'vendas'

urlpatterns = [
    path('', VendaListView.as_view(), name='venda_list'),
    path('novo/', venda_create, name='venda_create'),
    path('<int:pk>/', venda_detail, name='venda_detail'),
    path('<int:pk>/editar/', venda_update, name='venda_update'),
    path('<int:pk>/excluir/', venda_delete, name='venda_delete'),
]
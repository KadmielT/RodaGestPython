from django.urls import path

from .views import (
    ServicoListView,
    servico_create,
    servico_delete,
    servico_detail,
    servico_update,
)

app_name = 'servicos'

urlpatterns = [
    path('', ServicoListView.as_view(), name='servico_list'),
    path('novo/', servico_create, name='servico_create'),
    path('<int:pk>/', servico_detail, name='servico_detail'),
    path('<int:pk>/editar/', servico_update, name='servico_update'),
    path('<int:pk>/excluir/', servico_delete, name='servico_delete'),
]
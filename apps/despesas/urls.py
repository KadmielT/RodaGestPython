from django.urls import path

from .views import (
    DespesaListView,
    despesa_create,
    despesa_delete,
    despesa_detail,
    despesa_update,
)

app_name = 'despesas'

urlpatterns = [
    path('', DespesaListView.as_view(), name='despesa_list'),
    path('novo/', despesa_create, name='despesa_create'),
    path('<int:pk>/', despesa_detail, name='despesa_detail'),
    path('<int:pk>/editar/', despesa_update, name='despesa_update'),
    path('<int:pk>/excluir/', despesa_delete, name='despesa_delete'),
]
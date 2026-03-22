from django.urls import path

from .views import (
    RodaListView,
    movimentar_roda,
    roda_create,
    roda_delete,
    roda_detail,
    roda_update,
)

app_name = 'estoque_rodas'

urlpatterns = [
    path('', RodaListView.as_view(), name='roda_list'),
    path('nova/', roda_create, name='roda_create'),
    path('<int:pk>/', roda_detail, name='roda_detail'),
    path('<int:pk>/editar/', roda_update, name='roda_update'),
    path('<int:pk>/movimentar/', movimentar_roda, name='movimentar_roda'),
    path('<int:pk>/excluir/', roda_delete, name='roda_delete'),
]
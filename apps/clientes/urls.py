from django.urls import path
from .views import ClienteListView

urlpatterns = [
    path("", ClienteListView.as_view(), name="cliente_list"),
]
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", RedirectView.as_view(pattern_name="usuarios:login", permanent=False), name="home"),

    path("", include(("apps.usuarios.urls", "usuarios"), namespace="usuarios")),
    path("clientes/", include(("apps.clientes.urls", "clientes"), namespace="clientes")),
]
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", RedirectView.as_view(pattern_name="usuarios:login", permanent=False), name="home"),

    path("", include(("apps.usuarios.urls", "usuarios"), namespace="usuarios")),
    path("clientes/", include(("apps.clientes.urls", "clientes"), namespace="clientes")),
    path("estoque-rodas/", include(("apps.estoque_rodas.urls", "estoque_rodas"), namespace="estoque_rodas")),
    path("estoque-insumos/", include(("apps.estoque_insumos.urls", "estoque_insumos"), namespace="estoque_insumos")),
    path("servicos/", include(("apps.servicos.urls", "servicos"), namespace="servicos")),
    path("vendas/", include(("apps.vendas.urls", "vendas"), namespace="vendas")),
    path("despesas/", include(("apps.despesas.urls", "despesas"), namespace="despesas")),
    path("dashboard/", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
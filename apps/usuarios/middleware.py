from django.contrib import messages
from django.shortcuts import redirect

from .models import PermissaoUsuario


class RodaGestPermissaoMiddleware:
    MODULOS_POR_NAMESPACE = {
        "clientes": "acesso_clientes",
        "estoque_rodas": "acesso_estoque_rodas",
        "estoque_insumos": "acesso_estoque_insumos",
        "servicos": "acesso_servicos",
        "vendas": "acesso_vendas",
        "despesas": "acesso_despesas",
    }

    ROTAS_ADMIN_USUARIOS = {
        "usuario_admin_list",
        "usuario_admin_create",
        "usuario_admin_update",
        "usuario_admin_password_update",
        "usuario_admin_toggle_active",
        "usuario_admin_delete",
        "usuario_admin_send_password_reset",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.rg_permissoes = None

        if hasattr(request, "user") and request.user.is_authenticated:
            if not request.user.is_superuser:
                request.rg_permissoes, _ = PermissaoUsuario.objects.get_or_create(
                    usuario=request.user
                )

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not hasattr(request, "user"):
            return None

        if not request.user.is_authenticated:
            return None

        if request.user.is_superuser:
            return None

        resolver_match = getattr(request, "resolver_match", None)

        if not resolver_match:
            return None

        namespace = resolver_match.namespace
        url_name = resolver_match.url_name

        campo_permissao = None

        if namespace == "usuarios":
            if url_name not in self.ROTAS_ADMIN_USUARIOS:
                return None

            campo_permissao = "acesso_usuarios"

        else:
            campo_permissao = self.MODULOS_POR_NAMESPACE.get(namespace)

        if not campo_permissao:
            return None

        permissoes = request.rg_permissoes

        if not permissoes:
            permissoes, _ = PermissaoUsuario.objects.get_or_create(
                usuario=request.user
            )
            request.rg_permissoes = permissoes

        if getattr(permissoes, campo_permissao, False):
            return None

        messages.error(
            request,
            "Você não tem permissão para acessar este módulo."
        )

        return redirect("usuarios:perfil")
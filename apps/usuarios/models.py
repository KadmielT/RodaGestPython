from django.conf import settings
from django.db import models


class Perfil(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class PermissaoUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permissao_rodagest"
    )

    acesso_clientes = models.BooleanField(default=False)
    acesso_estoque_rodas = models.BooleanField(default=False)
    acesso_estoque_insumos = models.BooleanField(default=False)
    acesso_servicos = models.BooleanField(default=False)
    acesso_vendas = models.BooleanField(default=False)
    acesso_despesas = models.BooleanField(default=False)
    acesso_usuarios = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissões de {self.usuario.get_full_name() or self.usuario.username}"

    def pode_acessar(self, campo):
        if self.usuario.is_superuser:
            return True

        return getattr(self, campo, False)
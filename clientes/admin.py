from django.contrib import admin
from .models import Cliente, Endereco

class EnderecoInline(admin.StackedInline):
    model = Endereco
    can_delete = False
    extra = 0

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [EnderecoInline]
    # Mostra essas colunas na listagem (tela de "Clientes")
    list_display = ("nome", "tipo", "documento", "telefone", "email", "data_cadastro")

    # Cria barra de busca (pesquisa por nome, documento, telefone, email)
    search_fields = ("nome", "documento", "telefone", "email")

    # Define a ordem padrão (mais novo primeiro)
    ordering = ("-data_cadastro",)

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'cidade', 'uf', 'cep')
    search_fields = ('cliente__nome', 'cidade', 'bairro', 'cep')


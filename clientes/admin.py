from django.contrib import admin
from .models import Cliente, Endereco

class EnderecoInline(admin.StackedInline):
    model = Endereco
    can_delete = False
    extra = 0

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [EnderecoInline]

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'cidade', 'uf', 'cep')
    search_fields = ('cliente__nome', 'cidade', 'bairro', 'cep')

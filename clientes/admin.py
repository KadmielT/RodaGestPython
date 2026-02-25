from django.contrib import admin, messages
from .models import Cliente, Endereco

class EnderecoInline(admin.StackedInline):
    model = Endereco
    extra = 0
    can_delete = False

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [EnderecoInline]
    list_display = ("nome", "tipo", "documento", "telefone", "email", "data_cadastro")
    search_fields = ("nome", "documento", "telefone", "email")
    ordering = ("-data_cadastro",)

    actions = ["rg_delete_selected"]

    @admin.action(description="Excluir selecionados")
    def rg_delete_selected(self, request, queryset):
        total = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"{total} registro(s) excluído(s) com sucesso.",
            level=messages.SUCCESS
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Clientes"
        return super().changelist_view(request, extra_context=extra_context)
        
@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "cidade", "uf", "cep")
    search_fields = ("cliente__nome", "cidade", "bairro", "cep")
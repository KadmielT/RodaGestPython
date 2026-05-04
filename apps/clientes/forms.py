from django import forms
from .models import Cliente, Endereco
import re


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nome",
            "tipo",
            "documento",
            "telefone",
            "email",
            "observacoes",
        ]
        labels = {
            "nome": "Nome / Nome fantasia",
            "tipo": "Tipo",
            "documento": "CPF / CNPJ",
            "telefone": "Telefone",
            "email": "E-mail",
            "observacoes": "Observações",
        }
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o nome ou nome fantasia",
            }),
            "tipo": forms.Select(attrs={
                "class": "rg-input js-tom-select",
            }),
            "documento": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o CPF ou CNPJ",
            }),
            "telefone": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o telefone",
            }),
            "email": forms.EmailInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o e-mail",
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "rg-input",
                "placeholder": "Digite observações",
            }),
        }

    def clean_documento(self):
        documento = self.cleaned_data.get("documento", "")
        documento_limpo = re.sub(r"\D", "", documento)

        queryset = Cliente.objects.filter(documento=documento_limpo)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError("Já existe um cliente cadastrado com este CPF/CNPJ.")

        return documento_limpo


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = [
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "municipio",
            "estado",
        ]
        labels = {
            "cep": "CEP",
            "logradouro": "Logradouro",
            "numero": "Número",
            "complemento": "Complemento",
            "bairro": "Bairro",
            "municipio": "Município",
            "estado": "Estado",
        }
        widgets = {
            "cep": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o CEP",
            }),
            "logradouro": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o logradouro",
            }),
            "numero": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o número",
            }),
            "complemento": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o complemento",
            }),
            "bairro": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o bairro",
            }),
            "municipio": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "Digite o município",
            }),
            "estado": forms.TextInput(attrs={
                "class": "rg-input",
                "placeholder": "UF",
                "maxlength": "2",
            }),
        }
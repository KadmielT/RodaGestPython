import re
from django.db import models
from django.core.exceptions import ValidationError


TIPO_CHOICES = [
    ("PF", "Pessoa Física"),
    ("PJ", "Pessoa Jurídica"),
]

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES)
    documento = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.documento:
            self.documento = re.sub(r"\D", "", self.documento)

        if self.telefone:
            self.telefone = re.sub(r"\D", "", self.telefone)

        if self.tipo == "PF" and not self.validar_cpf(self.documento):
            raise ValidationError({"documento": "CPF inválido."})

        if self.tipo == "PJ" and not self.validar_cnpj(self.documento):
            raise ValidationError({"documento": "CNPJ inválido."})

        if self.telefone and len(self.telefone) not in [10, 11]:
            raise ValidationError({"telefone": "Telefone deve conter 10 ou 11 dígitos."})

    def validar_cpf(self, cpf):
        if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        dig1 = (soma * 10 % 11) % 10

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        dig2 = (soma * 10 % 11) % 10

        return dig1 == int(cpf[9]) and dig2 == int(cpf[10])

    def validar_cnpj(self, cnpj):
        if not cnpj or len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto = soma % 11
        dig1 = 0 if resto < 2 else 11 - resto

        pesos2 = [6] + pesos1
        soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto = soma % 11
        dig2 = 0 if resto < 2 else 11 - resto

        return cnpj[-2:] == f"{dig1}{dig2}"

    def __str__(self):
        return self.nome


class Endereco(models.Model):
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        related_name="endereco",
    )
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.cep:
            self.cep = re.sub(r"\D", "", self.cep)
            if len(self.cep) != 8:
                raise ValidationError({"cep": "CEP deve conter 8 dígitos."})

        if self.estado:
            self.estado = self.estado.upper()
            if len(self.estado) != 2:
                raise ValidationError({"estado": "Estado deve conter 2 caracteres."})

    def __str__(self):
        municipio = self.municipio if self.municipio else "-"
        estado = self.estado if self.estado else "-"
        return f"{self.cliente.nome} - {municipio}/{estado}"
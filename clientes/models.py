import re
from django.db import models
from django.core.exceptions import ValidationError


TIPO_CHOICES = [
    ('PF', 'Pessoa Física'),
    ('PJ', 'Pessoa Jurídica'),
]


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
    documento = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        #remove máscara
        if self.documento:
            self.documento = re.sub(r'\D', '', self.documento)

        if self.telefone:
            self.telefone = re.sub(r'\D', '', self.telefone)

        #Mensagem de erro conforme tipo
        if self.tipo == 'PF':
            if not self.validar_cpf(self.documento):
                raise ValidationError({'documento': 'CPF inválido.'})

        elif self.tipo == 'PJ':
            if not self.validar_cnpj(self.documento):
                raise ValidationError({'documento': 'CNPJ inválido.'})
            
        #Mensagem de erro do telefone
        if self.telefone: 
            if len(self.telefone) not in [10, 11]:
                raise ValidationError({'telefone': 'Telefone deve conter 10 ou 11 dígitos.'})

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

        pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
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
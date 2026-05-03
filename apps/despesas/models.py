from decimal import Decimal
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models


class Despesa(models.Model):
    class CategoriaChoices(models.TextChoices):
        AGUA = 'agua', 'Água'
        ENERGIA = 'energia', 'Energia'
        INTERNET = 'internet', 'Internet'
        TELEFONE = 'telefone', 'Telefone'
        ALUGUEL = 'aluguel', 'Aluguel'
        BOLETO = 'boleto', 'Boleto'
        FORNECEDOR = 'fornecedor', 'Fornecedor'
        MANUTENCAO = 'manutencao', 'Manutenção'
        IMPOSTO_TAXA = 'imposto_taxa', 'Imposto ou taxa'
        MATERIAL_CONSUMO = 'material_consumo', 'Material de consumo'
        SALARIO = 'salario', 'Salário'
        TRANSPORTE = 'transporte', 'Transporte'
        OUTROS = 'outros', 'Outros'

    class StatusChoices(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PAGA = 'paga', 'Paga'
        ATRASADA = 'atrasada', 'Atrasada'
        CANCELADA = 'cancelada', 'Cancelada'

    class FormaPagamentoChoices(models.TextChoices):
        DINHEIRO = 'dinheiro', 'Dinheiro'
        PIX = 'pix', 'Pix'
        CARTAO_DEBITO = 'cartao_debito', 'Cartão de débito'
        CARTAO_CREDITO = 'cartao_credito', 'Cartão de crédito'
        BOLETO = 'boleto', 'Boleto'
        TRANSFERENCIA = 'transferencia', 'Transferência'
        OUTROS = 'outros', 'Outros'

    descricao = models.CharField(max_length=150)

    categoria = models.CharField(
        max_length=30,
        choices=CategoriaChoices.choices,
        default=CategoriaChoices.OUTROS
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE
    )

    forma_pagamento = models.CharField(
        max_length=30,
        choices=FormaPagamentoChoices.choices,
        default=FormaPagamentoChoices.PIX
    )

    data_vencimento = models.DateField(blank=True, null=True)
    data_pagamento = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_cadastro']

    def __str__(self):
        return self.descricao

    def clean(self):
        super().clean()

        if self.descricao:
            self.descricao = self.descricao.strip()

        if self.valor is not None and self.valor <= 0:
            raise ValidationError({
                'valor': 'O valor da despesa deve ser maior que zero.'
            })

        if self.data_pagamento and self.data_vencimento:
            if (
                self.data_pagamento < self.data_vencimento
                and self.status == self.StatusChoices.ATRASADA
            ):
                raise ValidationError({
                    'status': 'Uma despesa paga antes do vencimento não deve ficar como atrasada.'
                })


class ArquivoDespesa(models.Model):
    despesa = models.ForeignKey(
        Despesa,
        on_delete=models.CASCADE,
        related_name='arquivos'
    )

    arquivo = models.FileField(upload_to='despesas/')
    nome_original = models.CharField(max_length=255, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Arquivo da despesa'
        verbose_name_plural = 'Arquivos da despesa'
        ordering = ['-data_cadastro']

    def __str__(self):
        return self.nome_arquivo

    @property
    def nome_arquivo(self):
        if self.nome_original:
            return self.nome_original

        return Path(self.arquivo.name).name

    @property
    def extensao(self):
        extensao = Path(self.nome_arquivo).suffix.replace('.', '').upper()

        if extensao:
            return extensao

        return 'ARQUIVO'

    @property
    def eh_imagem(self):
        return self.extensao.lower() in ['jpg', 'jpeg', 'png', 'webp', 'gif']
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Venda(models.Model):
    class StatusChoices(models.TextChoices):
        ORCAMENTO = 'orcamento', 'Orçamento'
        RESERVADA_NAO_PAGA = 'reservada_nao_paga', 'Reservada - não paga'
        RESERVADA_PAGA = 'reservada_paga', 'Reservada - paga'
        AGUARDANDO_PAGAMENTO = 'aguardando_pagamento', 'Aguardando pagamento'
        PAGA_AGUARDANDO_RETIRADA = 'paga_aguardando_retirada', 'Paga - aguardando retirada'
        PAGA_AGUARDANDO_ENTREGA = 'paga_aguardando_entrega', 'Paga - aguardando entrega'
        FINALIZADA_RETIRADA = 'finalizada_retirada', 'Finalizada - retirada pelo cliente'
        FINALIZADA_ENTREGUE = 'finalizada_entregue', 'Finalizada - entregue'
        CANCELADA = 'cancelada', 'Cancelada'

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='vendas'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=40,
        choices=StatusChoices.choices,
        default=StatusChoices.ORCAMENTO
    )
    data_venda = models.DateField(default=date.today)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda', '-data_cadastro']

    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()

        if self.valor_total < 0:
            raise ValidationError({
                'valor_total': 'O valor total da venda não pode ser negativo.'
            })

        if self.nome:
            self.nome = self.nome.strip()


class ItemVendaRoda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens_rodas'
    )
    roda = models.ForeignKey(
        'estoque_rodas.Roda',
        on_delete=models.PROTECT,
        related_name='itens_em_vendas'
    )
    quantidade = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de venda (roda)'
        verbose_name_plural = 'Itens de venda (rodas)'

    def __str__(self):
        return f'{self.roda.nome} - {self.quantidade}'

    def clean(self):
        super().clean()

        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'A quantidade deve ser maior que zero.'
            })


class ImagemVenda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='imagens'
    )
    imagem = models.ImageField(upload_to='vendas/')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem da venda'
        verbose_name_plural = 'Imagens da venda'
        ordering = ['data_cadastro']

    def __str__(self):
        return f'Imagem da venda {self.venda.nome}'
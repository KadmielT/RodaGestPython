from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Insumo(models.Model):
    class UnidadeMedidaChoices(models.TextChoices):
        UNIDADE = 'un', 'Unidade'
        QUILOGRAMA = 'kg', 'Quilograma'
        LITRO = 'l', 'Litro'
        METRO = 'm', 'Metro'
        CAIXA = 'cx', 'Caixa'
        PACOTE = 'pct', 'Pacote'

    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    quantidade = models.PositiveIntegerField(default=0)
    quantidade_inicial = models.PositiveIntegerField(default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    unidade_medida = models.CharField(
        max_length=10,
        choices=UnidadeMedidaChoices.choices,
        default=UnidadeMedidaChoices.UNIDADE
    )
    descricao = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'
        ordering = ['nome']

    def __str__(self):
        if self.codigo:
            return f'{self.nome} - {self.codigo}'
        return self.nome

    def clean(self):
        super().clean()

        if self.valor_unitario < 0:
            raise ValidationError({
                'valor_unitario': 'O valor por unidade não pode ser negativo.'
            })


class MovimentacaoInsumo(models.Model):
    class TipoMovimentacaoChoices(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name='movimentacoes'
    )
    tipo_movimentacao = models.CharField(
        max_length=10,
        choices=TipoMovimentacaoChoices.choices
    )
    quantidade = models.PositiveIntegerField()
    observacao = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de insumo'
        verbose_name_plural = 'Movimentações de insumos'
        ordering = ['-data_cadastro']

    def __str__(self):
        return f'{self.get_tipo_movimentacao_display()} - {self.insumo.nome}'

    def clean(self):
        super().clean()

        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'A quantidade deve ser maior que zero.'
            })

        if (
            self.tipo_movimentacao == self.TipoMovimentacaoChoices.SAIDA
            and self.insumo_id
            and self.quantidade > self.insumo.quantidade
        ):
            raise ValidationError({
                'quantidade': 'A saída não pode ser maior que a quantidade disponível em estoque.'
            })
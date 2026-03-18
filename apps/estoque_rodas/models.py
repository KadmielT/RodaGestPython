from django.core.exceptions import ValidationError
from django.db import models


class Roda(models.Model):
    class EstadoChoices(models.TextChoices):
        NOVA = 'nova', 'Nova'
        USADA = 'usada', 'Usada'
        REFORMADA = 'reformada', 'Reformada'

    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    quantidade = models.PositiveIntegerField(default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices
    )
    descricao = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Roda'
        verbose_name_plural = 'Rodas'
        ordering = ['nome']

    def __str__(self):
        if self.codigo:
            return f'{self.nome} - {self.codigo}'
        return self.nome

    def clean(self):
        super().clean()

        if self.quantidade < 0:
            raise ValidationError({
                'quantidade': 'A quantidade não pode ser negativa.'
            })

        if self.valor_unitario < 0:
            raise ValidationError({
                'valor_unitario': 'O valor por unidade não pode ser negativo.'
            })


class MovimentacaoRoda(models.Model):
    class TipoMovimentacaoChoices(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    roda = models.ForeignKey(
        Roda,
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
        verbose_name = 'Movimentação de roda'
        verbose_name_plural = 'Movimentações de rodas'
        ordering = ['-data_cadastro']

    def __str__(self):
        return f'{self.get_tipo_movimentacao_display()} - {self.roda.nome}'

    def clean(self):
        super().clean()

        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'A quantidade deve ser maior que zero.'
            })

        if (
            self.tipo_movimentacao == self.TipoMovimentacaoChoices.SAIDA
            and self.roda_id
            and self.quantidade > self.roda.quantidade
        ):
            raise ValidationError({
                'quantidade': 'A saída não pode ser maior que a quantidade disponível em estoque.'
            })
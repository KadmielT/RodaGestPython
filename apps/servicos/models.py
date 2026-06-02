from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Servico(models.Model):
    class StatusChoices(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        CONCLUIDO = 'concluido', 'Concluído'
        FINALIZADA_AGUARDANDO_CLIENTE = 'finalizada_aguardando_cliente', 'Finalizado - aguardando cliente'
        FINALIZADA_ENTREGUE = 'finalizada_entregue', 'Finalizado - entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='servicos'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=40,
        choices=StatusChoices.choices,
        default=StatusChoices.ABERTO
    )
    data_servico = models.DateField(default=date.today)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['-data_servico', '-data_cadastro']

    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()

        if self.valor_total < 0:
            raise ValidationError({
                'valor_total': 'O valor total do serviço não pode ser negativo.'
            })

        if self.nome:
            self.nome = self.nome.strip()


class ItemServicoRoda(models.Model):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name='itens_rodas'
    )
    roda = models.ForeignKey(
        'estoque_rodas.Roda',
        on_delete=models.PROTECT,
        related_name='itens_em_servicos'
    )
    quantidade = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de serviço (roda)'
        verbose_name_plural = 'Itens de serviço (rodas)'

    def __str__(self):
        return f'{self.roda.nome} - {self.quantidade}'

    def clean(self):
        super().clean()

        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'A quantidade deve ser maior que zero.'
            })


class ItemServicoInsumo(models.Model):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name='itens_insumos'
    )
    insumo = models.ForeignKey(
        'estoque_insumos.Insumo',
        on_delete=models.PROTECT,
        related_name='itens_em_servicos'
    )
    quantidade = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de serviço (insumo)'
        verbose_name_plural = 'Itens de serviço (insumos)'

    def __str__(self):
        return f'{self.insumo.nome} - {self.quantidade}'

    def clean(self):
        super().clean()

        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'A quantidade deve ser maior que zero.'
            })


class ImagemServico(models.Model):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name='imagens'
    )
    imagem = models.ImageField(upload_to='servicos/')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do serviço'
        verbose_name_plural = 'Imagens do serviço'
        ordering = ['data_cadastro']

    def __str__(self):
        return f'Imagem do serviço {self.servico.nome}'
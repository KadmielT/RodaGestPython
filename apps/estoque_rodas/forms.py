from decimal import Decimal, InvalidOperation

from django import forms

from .models import MovimentacaoRoda, Roda


class RodaForm(forms.ModelForm):
    valor_unitario = forms.CharField(
        label='Valor por unidade',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'rg-input js-money-br',
            'autocomplete': 'off',
            'inputmode': 'decimal',
        })
    )

    class Meta:
        model = Roda
        fields = ['nome', 'quantidade', 'valor_unitario', 'estado', 'codigo', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'rg-input',
                'placeholder': 'Digite o nome da roda',
                'style': 'width: 100%;',
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'rg-input js-only-integer',
                'min': 0,
                'step': 1,
                'placeholder': 'Digite a quantidade inicial',
                'inputmode': 'numeric',
            }),
            'estado': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'rg-input',
                'placeholder': 'Digite o código da roda (opcional)',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'rg-input',
                'rows': 6,
                'placeholder': 'Digite a descrição da roda (opcional)',
            }),
        }
        labels = {
            'nome': 'Nome da roda',
            'quantidade': 'Quantidade',
            'estado': 'Estado',
            'codigo': 'Código',
            'descricao': 'Descrição da roda',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.valor_unitario is not None:
            valor_decimal = self.instance.valor_unitario
            valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            self.initial['valor_unitario'] = f'R$ {valor_formatado}'
        else:
            valor_inicial = self.initial.get('valor_unitario')
            if valor_inicial not in (None, ''):
                try:
                    valor_decimal = Decimal(str(valor_inicial))
                    valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                    self.initial['valor_unitario'] = f'R$ {valor_formatado}'
                except (InvalidOperation, ValueError, TypeError):
                    self.initial['valor_unitario'] = 'R$ 0,00'
            else:
                self.initial['valor_unitario'] = 'R$ 0,00'

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')

        if codigo:
            return codigo.strip()

        return None

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')

        if nome:
            return nome.strip()

        return nome

    def clean_valor_unitario(self):
        valor = self.cleaned_data.get('valor_unitario')

        if valor in (None, ''):
            return Decimal('0.00')

        valor = str(valor).strip()
        valor = valor.replace('R$', '').replace(' ', '')

        try:
            valor_normalizado = valor.replace('.', '').replace(',', '.')
            valor_decimal = Decimal(valor_normalizado)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Informe um valor válido no formato brasileiro. Ex.: R$ 150,50')

        if valor_decimal < 0:
            raise forms.ValidationError('O valor por unidade não pode ser negativo.')

        return valor_decimal

class MovimentacaoRodaForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoRoda
        fields = ['tipo_movimentacao', 'quantidade', 'observacao']
        widgets = {
            'tipo_movimentacao': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'rg-input js-only-integer',
                'min': 1,
                'step': 1,
                'placeholder': 'Digite a quantidade',
                'inputmode': 'numeric',
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'rg-input',
                'rows': 4,
                'placeholder': 'Digite uma observação (opcional)',
            }),
        }
        labels = {
            'tipo_movimentacao': 'Tipo de movimentação',
            'quantidade': 'Quantidade',
            'observacao': 'Observação',
        }
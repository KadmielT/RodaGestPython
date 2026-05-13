from decimal import Decimal, InvalidOperation

from django import forms

from apps.clientes.models import Cliente
from apps.estoque_rodas.models import Roda

from .models import Venda, ItemVendaRoda, ImagemVenda


class VendaForm(forms.ModelForm):
    valor_total = forms.CharField(
        label='Valor total',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'rg-input js-money-br',
            'autocomplete': 'off',
            'inputmode': 'decimal',
        })
    )

    class Meta:
        model = Venda
        fields = ['cliente', 'nome', 'descricao', 'valor_total', 'status']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'nome': forms.TextInput(attrs={
                'class': 'rg-input',
                'placeholder': 'Digite o nome da venda',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'rg-input',
                'rows': 5,
                'placeholder': 'Digite a descrição da venda (opcional)',
            }),
            'status': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
        }
        labels = {
            'cliente': 'Cliente',
            'nome': 'Nome da venda',
            'descricao': 'Descrição',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cliente'].queryset = Cliente.objects.order_by('nome')
        self.fields['cliente'].empty_label = 'Selecione um cliente'

        if self.instance and self.instance.pk and self.instance.valor_total is not None:
            valor_decimal = self.instance.valor_total
            valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            self.initial['valor_total'] = f'R$ {valor_formatado}'
        else:
            valor_inicial = self.initial.get('valor_total')

            if valor_inicial not in (None, ''):
                try:
                    valor_decimal = Decimal(str(valor_inicial))
                    valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                    self.initial['valor_total'] = f'R$ {valor_formatado}'
                except (InvalidOperation, ValueError, TypeError):
                    self.initial['valor_total'] = 'R$ 0,00'
            else:
                self.initial['valor_total'] = 'R$ 0,00'

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')

        if nome:
            return nome.strip()

        return nome

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')

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
            raise forms.ValidationError('O valor total não pode ser negativo.')

        return valor_decimal


class ItemVendaRodaForm(forms.ModelForm):
    class Meta:
        model = ItemVendaRoda
        fields = ['roda', 'quantidade']
        widgets = {
            'roda': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'rg-input js-only-integer',
                'min': 1,
                'step': 1,
                'placeholder': 'Digite a quantidade',
                'inputmode': 'numeric',
            }),
        }
        labels = {
            'roda': 'Roda',
            'quantidade': 'Quantidade',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['roda'].queryset = Roda.objects.order_by('nome')
        self.fields['roda'].empty_label = 'Selecione uma roda'


class ItemVendaRodaInlineForm(forms.Form):
    roda = forms.ModelChoiceField(
        queryset=Roda.objects.none(),
        required=False,
        label='Roda',
        widget=forms.Select(attrs={
            'class': 'js-tom-select',
        })
    )
    quantidade = forms.IntegerField(
        required=False,
        label='Quantidade',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'rg-input js-only-integer',
            'min': 1,
            'step': 1,
            'placeholder': 'Digite a quantidade',
            'inputmode': 'numeric',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['roda'].queryset = Roda.objects.order_by('nome')
        self.fields['roda'].empty_label = 'Selecione uma roda'

    def clean(self):
        cleaned_data = super().clean()
        roda = cleaned_data.get('roda')
        quantidade = cleaned_data.get('quantidade')

        if roda and not quantidade:
            self.add_error('quantidade', 'Informe a quantidade da roda.')

        if quantidade and not roda:
            self.add_error('roda', 'Selecione uma roda.')

        return cleaned_data


class ImagemVendaForm(forms.ModelForm):
    class Meta:
        model = ImagemVenda
        fields = ['imagem']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={
                'class': 'rg-input',
                'accept': 'image/*',
            }),
        }
        labels = {
            'imagem': 'Imagem',
        }
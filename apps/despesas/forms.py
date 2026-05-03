from decimal import Decimal, InvalidOperation

from django import forms

from .models import Despesa


class DespesaForm(forms.ModelForm):
    valor = forms.CharField(
        label='Valor',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'rg-input js-money-br',
            'autocomplete': 'off',
            'inputmode': 'decimal',
        })
    )

    class Meta:
        model = Despesa
        fields = [
            'descricao',
            'categoria',
            'valor',
            'status',
            'forma_pagamento',
            'data_vencimento',
            'data_pagamento',
            'observacoes',
        ]

        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'rg-input',
                'placeholder': 'Ex.: Conta de energia, internet, boleto...',
            }),
            'categoria': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'status': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'js-tom-select',
            }),
            'data_vencimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'rg-input',
                    'type': 'date',
                }
            ),
            'data_pagamento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'rg-input',
                    'type': 'date',
                }
            ),
            'observacoes': forms.Textarea(attrs={
                'class': 'rg-input',
                'rows': 5,
                'placeholder': 'Digite observações sobre a despesa (opcional)',
            }),
        }

        labels = {
            'descricao': 'Descrição da despesa',
            'categoria': 'Categoria',
            'status': 'Status',
            'forma_pagamento': 'Forma de pagamento',
            'data_vencimento': 'Data de vencimento',
            'data_pagamento': 'Data de pagamento',
            'observacoes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_vencimento'].input_formats = ['%Y-%m-%d']
        self.fields['data_pagamento'].input_formats = ['%Y-%m-%d']

        if self.instance and self.instance.pk:
            if self.instance.data_vencimento:
                self.initial['data_vencimento'] = self.instance.data_vencimento.strftime('%Y-%m-%d')

            if self.instance.data_pagamento:
                self.initial['data_pagamento'] = self.instance.data_pagamento.strftime('%Y-%m-%d')

            if self.instance.valor is not None:
                valor_decimal = self.instance.valor
                valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                self.initial['valor'] = f'R$ {valor_formatado}'
        else:
            valor_inicial = self.initial.get('valor')

            if valor_inicial not in (None, ''):
                try:
                    valor_decimal = Decimal(str(valor_inicial))
                    valor_formatado = f'{valor_decimal:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
                    self.initial['valor'] = f'R$ {valor_formatado}'
                except (InvalidOperation, ValueError, TypeError):
                    self.initial['valor'] = 'R$ 0,00'
            else:
                self.initial['valor'] = 'R$ 0,00'

    def clean_descricao(self):
        descricao = self.cleaned_data.get('descricao')

        if descricao:
            return descricao.strip()

        return descricao

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

        if valor in (None, ''):
            raise forms.ValidationError('Informe o valor da despesa.')

        valor = str(valor).strip()
        valor = valor.replace('R$', '').replace(' ', '')

        try:
            valor_normalizado = valor.replace('.', '').replace(',', '.')
            valor_decimal = Decimal(valor_normalizado)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Informe um valor válido no formato brasileiro. Ex.: R$ 150,50')

        if valor_decimal <= 0:
            raise forms.ValidationError('O valor da despesa deve ser maior que zero.')

        return valor_decimal

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get('status')
        data_pagamento = cleaned_data.get('data_pagamento')

        if status == Despesa.StatusChoices.PAGA and not data_pagamento:
            self.add_error('data_pagamento', 'Informe a data de pagamento para despesas pagas.')

        return cleaned_data
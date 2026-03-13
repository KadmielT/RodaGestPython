from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite seu e-mail",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )

class RodaGestPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget = forms.EmailInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite o seu e-mail",
                "autocomplete": "email",
            }
        )
        self.fields["email"].label = "E-mail"

class RodaGestSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields["new_password1"].widget.attrs.update({
            "class": "rg-input",
            "placeholder": "Digite sua nova senha",
            "autocomplete": "new-password",
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "rg-input",
            "placeholder": "Confirme sua nova senha",
            "autocomplete": "new-password",
        })

        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmar senha"
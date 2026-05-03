from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm


User = get_user_model()


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

        self.fields["new_password1"].widget = forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Digite sua nova senha",
                "autocomplete": "new-password",
            }
        )

        self.fields["new_password2"].widget = forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Confirme sua nova senha",
                "autocomplete": "new-password",
            }
        )

        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmar senha"


class PerfilUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome completo",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite seu nome completo",
                "autocomplete": "name",
            }
        ),
    )

    email = forms.EmailField(
        label="E-mail",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite seu e-mail",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "email"]

    def clean_first_name(self):
        nome_completo = self.cleaned_data.get("first_name", "").strip()

        if not nome_completo:
            raise forms.ValidationError("Informe seu nome completo.")

        return nome_completo

    def clean_email(self):
        email = self.cleaned_data.get("email", "")

        if not email:
            raise forms.ValidationError("Informe um e-mail válido.")

        email = email.strip().lower()

        usuarios_com_mesmo_email = User.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            usuarios_com_mesmo_email = usuarios_com_mesmo_email.exclude(pk=self.instance.pk)

        if usuarios_com_mesmo_email.exists():
            raise forms.ValidationError("Este e-mail já está sendo usado por outro usuário.")

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.last_name = ""

        if commit:
            usuario.save()

        return usuario


class RodaGestPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields["old_password"].widget = forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Digite sua senha atual",
                "autocomplete": "current-password",
            }
        )

        self.fields["new_password1"].widget = forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Digite sua nova senha",
                "autocomplete": "new-password",
            }
        )

        self.fields["new_password2"].widget = forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Confirme sua nova senha",
                "autocomplete": "new-password",
            }
        )

        self.fields["old_password"].label = "Senha atual"
        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmar nova senha"
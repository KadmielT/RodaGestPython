import re

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm

from .models import PermissaoUsuario


User = get_user_model()


def gerar_username_por_email(email):
    base = email.split("@")[0].strip().lower()
    base = re.sub(r"[^a-zA-Z0-9_@+.-]", "", base)

    if not base:
        base = "usuario"

    base = base[:140]
    username = base
    contador = 1

    while User.objects.filter(username=username).exists():
        username = f"{base}{contador}"
        contador += 1

    return username


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


class PermissaoUsuarioForm(forms.ModelForm):
    acesso_clientes = forms.BooleanField(
        label="Clientes",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_estoque_rodas = forms.BooleanField(
        label="Estoque de rodas",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_estoque_insumos = forms.BooleanField(
        label="Estoque de insumos",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_servicos = forms.BooleanField(
        label="Serviços",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_vendas = forms.BooleanField(
        label="Vendas",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_despesas = forms.BooleanField(
        label="Despesas",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    acesso_usuarios = forms.BooleanField(
        label="Administração de usuários",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rg-checkbox"})
    )

    class Meta:
        model = PermissaoUsuario
        fields = [
            "acesso_clientes",
            "acesso_estoque_rodas",
            "acesso_estoque_insumos",
            "acesso_servicos",
            "acesso_vendas",
            "acesso_despesas",
            "acesso_usuarios",
        ]


class UsuarioAdminCreateForm(forms.ModelForm):
    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("ativo", "Ativo"),
            ("inativo", "Inativo"),
        ],
        initial="ativo",
        widget=forms.Select(attrs={
            "class": "js-usuario-status-select",
            "data-placeholder": "Selecione o status",
        })
    )

    password1 = forms.CharField(
        label="Senha inicial",
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Digite a senha inicial",
                "autocomplete": "new-password",
            }
        )
    )

    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Confirme a senha inicial",
                "autocomplete": "new-password",
            }
        )
    )

    first_name = forms.CharField(
        label="Nome completo",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite o nome completo",
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
                "placeholder": "Digite o e-mail de acesso",
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
            raise forms.ValidationError("Informe o nome completo.")

        return nome_completo

    def clean_email(self):
        email = self.cleaned_data.get("email", "")

        if not email:
            raise forms.ValidationError("Informe um e-mail válido.")

        email = email.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está sendo usado por outro usuário.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não conferem.")

        if password1:
            try:
                password_validation.validate_password(password1)
            except forms.ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.username = gerar_username_por_email(usuario.email)
        usuario.last_name = ""
        usuario.is_active = self.cleaned_data.get("status") == "ativo"
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.set_password(self.cleaned_data["password1"])

        if commit:
            usuario.save()

        return usuario


class UsuarioAdminUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome completo",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "rg-input",
                "placeholder": "Digite o nome completo",
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
                "placeholder": "Digite o e-mail de acesso",
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
            raise forms.ValidationError("Informe o nome completo.")

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

        if usuario.is_superuser:
            usuario.is_active = True

        if commit:
            usuario.save()

        return usuario


class UsuarioAdminPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Digite a nova senha",
                "autocomplete": "new-password",
            }
        )
    )

    password2 = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "class": "rg-input",
                "placeholder": "Confirme a nova senha",
                "autocomplete": "new-password",
            }
        )
    )

    def __init__(self, usuario, *args, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não conferem.")

        if password1:
            try:
                password_validation.validate_password(password1, self.usuario)
            except forms.ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data

    def save(self):
        nova_senha = self.cleaned_data["password1"]

        self.usuario.set_password(nova_senha)
        self.usuario.save()

        return self.usuario
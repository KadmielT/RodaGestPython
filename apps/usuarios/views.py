from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .forms import LoginForm


User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("clientes:cliente_list")

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                usuario = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                usuario = None
            except User.MultipleObjectsReturned:
                usuario = User.objects.filter(email__iexact=email).first()

            if usuario is not None:
                user = authenticate(
                    request,
                    username=usuario.username,
                    password=password
                )

                if user is not None:
                    login(request, user)
                    messages.success(request, f"Bem-vindo, {user.get_username()}!")
                    return redirect("clientes:cliente_list")

            messages.error(request, "E-mail ou senha inválidos.")

    return render(request, "usuarios/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Você saiu do sistema com sucesso.")
        return redirect("usuarios:login")

    return redirect("clientes:cliente_list")
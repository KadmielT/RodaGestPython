from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, PerfilUsuarioForm, RodaGestPasswordChangeForm


User = get_user_model()


def form_errors_to_dict(form):
    errors = {}

    for field, field_errors in form.errors.items():
        errors[field] = [str(error) for error in field_errors]

    return errors


def is_ajax_request(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


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


@login_required
def perfil_view(request):
    usuario = request.user

    perfil_form = PerfilUsuarioForm(instance=usuario)
    senha_form = RodaGestPasswordChangeForm(usuario)

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "atualizar_perfil":
            perfil_form = PerfilUsuarioForm(request.POST, instance=usuario)

            if perfil_form.is_valid():
                perfil_form.save()

                messages.success(request, "Seu perfil foi atualizado com sucesso.")
                return redirect("usuarios:perfil")

            messages.error(
                request,
                "Não foi possível atualizar seu perfil. Revise os campos informados."
            )

        elif acao == "alterar_senha":
            senha_form = RodaGestPasswordChangeForm(usuario, request.POST)

            if senha_form.is_valid():
                usuario = senha_form.save()

                update_session_auth_hash(request, usuario)

                messages.success(request, "Sua senha foi alterada com sucesso.")

                if is_ajax_request(request):
                    return JsonResponse({
                        "success": True,
                        "redirect_url": request.path,
                    })

                return redirect("usuarios:perfil")

            if is_ajax_request(request):
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Não foi possível alterar sua senha. Revise os campos informados.",
                        "errors": form_errors_to_dict(senha_form),
                    },
                    status=400
                )

            messages.error(
                request,
                "Não foi possível alterar sua senha. Revise os campos informados."
            )

    context = {
        "perfil_form": perfil_form,
        "senha_form": senha_form,
        "usuario": usuario,
        "breadcrumbs": [
            {"label": "Usuário"},
            {"label": "Meu perfil"},
        ],
    }

    return render(request, "usuarios/perfil.html", context)
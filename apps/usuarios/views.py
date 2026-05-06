from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import (
    LoginForm,
    PerfilUsuarioForm,
    RodaGestPasswordChangeForm,
    RodaGestPasswordResetForm,
    PermissaoUsuarioForm,
    UsuarioAdminCreateForm,
    UsuarioAdminPasswordForm,
    UsuarioAdminUpdateForm,
)
from .models import PermissaoUsuario


User = get_user_model()


ROTAS_POR_PERMISSAO = [
    ("acesso_clientes", "clientes:cliente_list"),
    ("acesso_estoque_rodas", "estoque_rodas:roda_list"),
    ("acesso_estoque_insumos", "estoque_insumos:insumo_list"),
    ("acesso_servicos", "servicos:servico_list"),
    ("acesso_vendas", "vendas:venda_list"),
    ("acesso_despesas", "despesas:despesa_list"),
    ("acesso_usuarios", "usuarios:usuario_admin_list"),
]


def form_errors_to_dict(form):
    errors = {}

    for field, field_errors in form.errors.items():
        errors[field] = [str(error) for error in field_errors]

    return errors


def is_ajax_request(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def get_permissoes_usuario(usuario):
    if not usuario.is_authenticated:
        return None

    if usuario.is_superuser:
        return None

    permissoes, _ = PermissaoUsuario.objects.get_or_create(usuario=usuario)

    return permissoes


def usuario_tem_permissao(usuario, campo):
    if not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    permissoes = get_permissoes_usuario(usuario)

    if not permissoes:
        return False

    return getattr(permissoes, campo, False)


def get_primeira_rota_permitida(usuario):
    if not usuario.is_authenticated:
        return "usuarios:login"

    if usuario.is_superuser:
        return "dashboard:home"

    permissoes = get_permissoes_usuario(usuario)

    if not permissoes:
        return "usuarios:perfil"

    for campo, _rota in ROTAS_POR_PERMISSAO:
        if getattr(permissoes, campo, False):
            return "dashboard:home"

    return "usuarios:perfil"


def usuario_admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not usuario_tem_permissao(request.user, "acesso_usuarios"):
            messages.error(request, "Você não tem permissão para acessar a administração de usuários.")
            return redirect(get_primeira_rota_permitida(request.user))

        return view_func(request, *args, **kwargs)

    return wrapper


def proteger_adm_master_de_outro_usuario(request, usuario_alvo):
    if usuario_alvo.is_superuser and usuario_alvo.pk != request.user.pk:
        messages.error(
            request,
            "O ADM MASTER não pode ser alterado por outro usuário."
        )
        return True

    return False


def bloquear_acao_perigosa(request, usuario_alvo, acao):
    if usuario_alvo.pk == request.user.pk:
        messages.error(
            request,
            f"Você não pode {acao} o próprio usuário logado."
        )
        return True

    if usuario_alvo.is_superuser:
        messages.error(
            request,
            f"O ADM MASTER não pode ser {acao} pela administração."
        )
        return True

    return False


def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_primeira_rota_permitida(request.user))

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
                    return redirect(get_primeira_rota_permitida(user))

            messages.error(request, "E-mail ou senha inválidos.")

    return render(request, "usuarios/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Você saiu do sistema com sucesso.")
        return redirect("usuarios:login")

    return redirect(get_primeira_rota_permitida(request.user))


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


class UsuarioAdminListView(ListView):
    model = User
    template_name = "usuarios/administracao/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("usuarios:login")

        if not usuario_tem_permissao(request.user, "acesso_usuarios"):
            messages.error(request, "Você não tem permissão para acessar a administração de usuários.")
            return redirect(get_primeira_rota_permitida(request.user))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.all().order_by("-is_superuser", "-is_active", "first_name", "username")
        busca = self.request.GET.get("q", "").strip()

        if busca:
            queryset = queryset.filter(
                Q(first_name__icontains=busca) |
                Q(username__icontains=busca) |
                Q(email__icontains=busca)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["breadcrumbs"] = [
            {"label": "Administração"},
            {"label": "Usuários"},
        ]

        return context


@usuario_admin_required
def usuario_admin_create(request):
    if request.method == "POST":
        form = UsuarioAdminCreateForm(request.POST)
        permissao_form = PermissaoUsuarioForm(request.POST)

        if form.is_valid() and permissao_form.is_valid():
            usuario = form.save()

            permissoes = permissao_form.save(commit=False)
            permissoes.usuario = usuario
            permissoes.save()

            messages.success(
                request,
                f'Usuário "{usuario.first_name or usuario.username}" foi cadastrado com sucesso.'
            )
            return redirect("usuarios:usuario_admin_list")

        messages.error(request, "Não foi possível cadastrar o usuário. Revise os campos informados.")
    else:
        form = UsuarioAdminCreateForm()
        permissao_form = PermissaoUsuarioForm()

    context = {
        "form": form,
        "permissao_form": permissao_form,
        "modo_edicao": False,
        "titulo": "Novo usuário",
        "breadcrumbs": [
            {"label": "Administração"},
            {"label": "Usuários", "url": "/administracao/usuarios/"},
            {"label": "Novo usuário"},
        ],
    }

    return render(request, "usuarios/administracao/usuario_form.html", context)


@usuario_admin_required
def usuario_admin_update(request, pk):
    usuario_alvo = get_object_or_404(User, pk=pk)

    if proteger_adm_master_de_outro_usuario(request, usuario_alvo):
        return redirect("usuarios:usuario_admin_list")

    permissao = None

    if not usuario_alvo.is_superuser:
        permissao, _ = PermissaoUsuario.objects.get_or_create(usuario=usuario_alvo)

    if request.method == "POST":
        form = UsuarioAdminUpdateForm(request.POST, instance=usuario_alvo)

        if usuario_alvo.is_superuser:
            permissao_form = None

            if form.is_valid():
                usuario = form.save()

                messages.success(
                    request,
                    f'Usuário "{usuario.first_name or usuario.username}" foi atualizado com sucesso.'
                )
                return redirect("usuarios:usuario_admin_list")

        else:
            permissao_form = PermissaoUsuarioForm(request.POST, instance=permissao)

            if form.is_valid() and permissao_form.is_valid():
                usuario = form.save()
                permissao_form.save()

                messages.success(
                    request,
                    f'Usuário "{usuario.first_name or usuario.username}" foi atualizado com sucesso.'
                )
                return redirect("usuarios:usuario_admin_list")

        messages.error(request, "Não foi possível atualizar o usuário. Revise os campos informados.")
    else:
        form = UsuarioAdminUpdateForm(instance=usuario_alvo)
        permissao_form = None

        if not usuario_alvo.is_superuser:
            permissao_form = PermissaoUsuarioForm(instance=permissao)

    context = {
        "form": form,
        "permissao_form": permissao_form,
        "usuario_alvo": usuario_alvo,
        "modo_edicao": True,
        "titulo": "Editar usuário",
        "breadcrumbs": [
            {"label": "Administração"},
            {"label": "Usuários", "url": "/administracao/usuarios/"},
            {"label": usuario_alvo.first_name or usuario_alvo.username},
            {"label": "Editar"},
        ],
    }

    return render(request, "usuarios/administracao/usuario_form.html", context)


@usuario_admin_required
def usuario_admin_password_update(request, pk):
    usuario_alvo = get_object_or_404(User, pk=pk)

    if proteger_adm_master_de_outro_usuario(request, usuario_alvo):
        return redirect("usuarios:usuario_admin_list")

    if request.method == "POST":
        form = UsuarioAdminPasswordForm(usuario_alvo, request.POST)

        if form.is_valid():
            usuario = form.save()

            if usuario.pk == request.user.pk:
                update_session_auth_hash(request, usuario)

            messages.success(
                request,
                f'A senha do usuário "{usuario.first_name or usuario.username}" foi alterada com sucesso.'
            )
            return redirect("usuarios:usuario_admin_list")

        messages.error(request, "Não foi possível alterar a senha. Revise os campos informados.")
    else:
        form = UsuarioAdminPasswordForm(usuario_alvo)

    context = {
        "form": form,
        "usuario_alvo": usuario_alvo,
        "breadcrumbs": [
            {"label": "Administração"},
            {"label": "Usuários", "url": "/administracao/usuarios/"},
            {"label": usuario_alvo.first_name or usuario_alvo.username},
            {"label": "Alterar senha"},
        ],
    }

    return render(request, "usuarios/administracao/usuario_password_form.html", context)


@usuario_admin_required
def usuario_admin_toggle_active(request, pk):
    usuario_alvo = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        if bloquear_acao_perigosa(request, usuario_alvo, "inativar/ativar"):
            return redirect("usuarios:usuario_admin_list")

        usuario_alvo.is_active = not usuario_alvo.is_active
        usuario_alvo.save(update_fields=["is_active"])

        status = "ativado" if usuario_alvo.is_active else "inativado"

        messages.success(
            request,
            f'Usuário "{usuario_alvo.first_name or usuario_alvo.username}" foi {status} com sucesso.'
        )

    return redirect("usuarios:usuario_admin_list")


@usuario_admin_required
def usuario_admin_delete(request, pk):
    usuario_alvo = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        if bloquear_acao_perigosa(request, usuario_alvo, "excluir"):
            return redirect("usuarios:usuario_admin_list")

        nome_usuario = usuario_alvo.first_name or usuario_alvo.username
        usuario_alvo.delete()

        messages.success(
            request,
            f'Usuário "{nome_usuario}" foi excluído permanentemente.'
        )

    return redirect("usuarios:usuario_admin_list")


@usuario_admin_required
def usuario_admin_send_password_reset(request, pk):
    usuario_alvo = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        if proteger_adm_master_de_outro_usuario(request, usuario_alvo):
            return redirect("usuarios:usuario_admin_list")

        if not usuario_alvo.email:
            messages.error(request, "Este usuário não possui e-mail cadastrado.")
            return redirect("usuarios:usuario_admin_list")

        if not usuario_alvo.is_active:
            messages.error(request, "Não é possível enviar recuperação para usuário inativo.")
            return redirect("usuarios:usuario_admin_list")

        reset_form = RodaGestPasswordResetForm({"email": usuario_alvo.email})

        if reset_form.is_valid():
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="usuarios/password_reset_email.html",
                subject_template_name="usuarios/password_reset_subject.txt",
            )

            messages.success(
                request,
                f'E-mail de recuperação enviado para "{usuario_alvo.email}".'
            )
        else:
            messages.error(request, "Não foi possível enviar o e-mail de recuperação.")

    return redirect("usuarios:usuario_admin_list")
from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    login_view,
    logout_view,
    perfil_view,
    UsuarioAdminListView,
    usuario_admin_create,
    usuario_admin_update,
    usuario_admin_password_update,
    usuario_admin_toggle_active,
    usuario_admin_delete,
    usuario_admin_send_password_reset,
)
from .forms import RodaGestPasswordResetForm, RodaGestSetPasswordForm

app_name = "usuarios"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("perfil/", perfil_view, name="perfil"),

    path("administracao/usuarios/", UsuarioAdminListView.as_view(), name="usuario_admin_list"),
    path("administracao/usuarios/novo/", usuario_admin_create, name="usuario_admin_create"),
    path("administracao/usuarios/<int:pk>/editar/", usuario_admin_update, name="usuario_admin_update"),
    path("administracao/usuarios/<int:pk>/senha/", usuario_admin_password_update, name="usuario_admin_password_update"),
    path("administracao/usuarios/<int:pk>/status/", usuario_admin_toggle_active, name="usuario_admin_toggle_active"),
    path("administracao/usuarios/<int:pk>/excluir/", usuario_admin_delete, name="usuario_admin_delete"),
    path("administracao/usuarios/<int:pk>/enviar-recuperacao/", usuario_admin_send_password_reset, name="usuario_admin_send_password_reset"),

    path(
        "esqueceu-senha/",
        auth_views.PasswordResetView.as_view(
            form_class=RodaGestPasswordResetForm,
            template_name="usuarios/password_reset_form.html",
            email_template_name="usuarios/password_reset_email.html",
            subject_template_name="usuarios/password_reset_subject.txt",
            success_url="/esqueceu-senha/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "esqueceu-senha/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "redefinir/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=RodaGestSetPasswordForm,
            template_name="usuarios/password_reset_confirm.html",
            success_url="/redefinir/concluido/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "redefinir/concluido/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
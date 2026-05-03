from django.urls import path
from django.contrib.auth import views as auth_views

from .views import login_view, logout_view, perfil_view
from .forms import RodaGestPasswordResetForm, RodaGestSetPasswordForm

app_name = "usuarios"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("perfil/", perfil_view, name="perfil"),

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
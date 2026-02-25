from django.apps import AppConfig
from apps.core.admin import BaseAdmin

class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.usuarios"
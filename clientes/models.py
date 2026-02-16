from django.db import models

TIPO_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
] 

class Cliente(models.Model):
        nome = models.CharField(max_length=150)
        tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
        documento = models.CharField(max_length=20, unique=True)
        telefone = models.CharField(max_length=20, unique=True)
        email = models.EmailField(blank=True, null=True)
        data_cadastro = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.nome

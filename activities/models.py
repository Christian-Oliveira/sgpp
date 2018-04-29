from django.db import models
from projects.models import Project
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class Activity(models.Model):
    """
    Permite gerenciar (Inserir, Excluir, Alterar, Consultar) as atividades que serão desempenhadas no projeto,
    deve ser informado um nome e descricao ao associar ao projeto.
    """

    name = models.CharField(max_length=50)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')

    """
    O orçamento da atividade deve obedecer o limite máximo do orçamento restante do projeto
    """
    budget = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return self.name
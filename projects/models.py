from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

from indicators.models import Indicator

# Create your models here.
User = get_user_model()


class ProjectQuerySet(models.query.QuerySet):

    def active(self):
        return self.exclude(status=8).order_by('rating','-start_date')

    def search(self, query):
        lookups = (
            Q(manager__username__icontains=query) |
            Q(name__icontains=query)
        )
        return self.filter(lookups).distinct()


class ProjectManager(models.Manager):

    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)


class Project(models.Model):

    """
    O sistema deve permitir o cadastro (inserção, exclusão, alteração e consulta) de projetos. Para cada projeto
    devem ser informados: nome, data de início, gerente responsável, previsão de término, data real de
    término, orçamento total, descrição e status. Os projetos devem ser classificados em: baixo risco, médio
    risco e alto risco. A classificação de risco não é cadastrada no sistema. Os status possíveis não são
    cadastrados no sistema. Os status possíveis são: em análise, análise realizada, análise aprovada, iniciado,
    planejado, em andamento, encerrado, cancelado.
    """

    STATUS_CHOICES = (
        (1, 'Em Análise'),
        (2, 'Análise Realizada'),
        (3, 'Análise Aprovada'),
        (4, 'Iniciado'),
        (5, 'Planejado'),
        (6, 'Em Andamento'),
        (7, 'Encerrado'),
        (8, 'Cancelado'),
    )

    RATING_CHOICES = (
        (1, 'Baixo'),
        (2, 'Médio'),
        (3, 'Alto'),
    )

    name = models.CharField(max_length=140)
    description = models.TextField()
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='manager')
    leader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='leader')
    start_date = models.DateField()
    forecast_finish_date = models.DateField()
    end_date = models.DateField(null=True)
    budget = models.DecimalField(max_digits=9, decimal_places=2, validators=[
                                 MinValueValidator(Decimal('0.01'))])
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=1)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    modified = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    def __str__(self):
        return self.name


class ProjectTeam(models.Model):
    """
    O sistema deve permitir se cadastrar e gerenciar os nomes dos membros da equipe do projeto.
    """
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='team')
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name


class ProjectIndicator(models.Model):
    """
    O sistema deve permitir associar indicadores a serem acompanhados em um projeto. Ao associar um
    indicador ao projeto, deve ser possível informar os valores esperados mínimo e máximo para o mesmo.
    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='indicators')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    max_value = models.PositiveIntegerField()
    min_value = models.PositiveIntegerField()


class ProjectIndicatorMonitor(models.Model):
    """
    O sistema deve permitir informar um indicador de um projeto a qualquer momento. Os indicadores devem
    ser associados a fases do projeto.
    """

    PHASE_CHOICES = (
        (1, 'Iniciação'),  # em análise, análise realizada, análise aprovada, 
        (2, 'Planejamento'),  # iniciado, planejado
        (3, 'Execução'),  # em andamento
        (4, 'Finalização')  # encerrado
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='indicator_monitor')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    phase = models.PositiveSmallIntegerField(choices=PHASE_CHOICES)
    value = models.PositiveIntegerField()


class ProjectStatusMonitor(models.Model):
    """
    O sistema deve permitir alterar o status dos projetos. Ao alterar o status do projeto para 'análise
    aprovada', o sistema deve exigir o preenchimento de uma justificativa assim como na transição para o
    status 'cancelado'. A cada alteração de status, o sistema deve registrar o último responsável e data da
    alteração.
    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='status_monitor')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    status = models.PositiveSmallIntegerField(choices=Project.STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)


class ProjectFollowUp(models.Model):
    """
    O sistema deve exigir que, para projetos de alto risco, seja registrado o acompanhamento semanal do projeto. 
    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='follow_ups')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateField(default=timezone.now)

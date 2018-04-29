from django.db import models
from django.db.models import Q
# Create your models here.


class IndicatorQuerySet(models.query.QuerySet):

    def search(self, query):
        lookups = (
            Q(name__icontains=query)
        )
        return self.filter(lookups, is_active=True).distinct()


class IndicatorManager(models.Manager):

    def get_queryset(self):
        return IndicatorQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)


class Indicator(models.Model):
    """
    O sistema deve permitir o cadastro de indicadores (inserção, exclusão, alteração e consulta). Cada indicador
    deve ter um nome.
    """

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    objects = IndicatorManager()

    def __str__(self):
        return self.name
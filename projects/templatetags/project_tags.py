from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='in_list')
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


@register.filter(name='get_status_css_class')
def get_status_css_class(self):
        """
        Return the boostrap class corresponding to the status.
        """
        if self.status == 1:#Em Análise
            return "light"
        elif self.status == 2:#Análise Realizada
            return "dark"
        elif self.status == 3:#Análise Aprovada
            return "info"
        elif self.status == 4:#Iniciado
            return "secondary"
        elif self.status == 5:#Planejado
            return "primary"
        elif self.status == 6:#Em Andamento
            return "warning"
        elif self.status == 7:#Encerrado
            return "success"
        elif self.status == 8:#Cancelado
            return "danger"
        else:
            return ""


@register.filter(name='get_message_css_class')
def get_message_css_class(self):
        """
        Return the boostrap class corresponding to the status.
        """
        if self.tags == 'info':
            return "info"
        elif self.tags == 'success':
            return "success"
        elif self.tags == 'warning':
            return "warning"
        elif self.tags == 'error':
            return "danger"
        else:
            return ""


@register.filter(name='get_rating_css_class')
def get_rating_css_class(self):
        """
        Return the boostrap class corresponding to the rating.
        """
        if self.rating == 1:
            return "primary"
        elif self.rating == 2:
            return "warning"
        elif self.rating == 3:
            return "danger"
        else:
            return ""

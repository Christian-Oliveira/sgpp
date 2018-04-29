import datetime
from django import forms
from django.contrib.auth.models import User

from .models import (Project, ProjectFollowUp, ProjectIndicator,
                     ProjectIndicatorMonitor, ProjectStatusMonitor, ProjectTeam)
from indicators.models import Indicator
from activities.models import Activity


class NewProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'manager', 'leader', 'start_date',
                  'forecast_finish_date', 'budget', 'rating']
        labels = {
            'name': ('Nome'),
            'description': ('Descrição'),
            'manager': ('Gerente'),
            'leader': ('Líder do Projeto'),
            'start_date': ('Data de Início'),
            'forecast_finish_date': ('Previsão de Término'),
            'budget': ('Orçamento'),
            'rating': ('Classificação')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(
            is_active=True).order_by('username')
        self.fields['leader'].queryset = User.objects.filter(
            is_active=True).order_by('username')
        self.fields['rating'].choices = Project.RATING_CHOICES

    def clean_name(self):
        cleaned_data = super(NewProjectForm, self).clean()

        data = cleaned_data.get('name')

        n = Project.objects.filter(name=data)

        if n.exists():
            raise forms.ValidationError('Nome do Projeto já está sendo usado.')

        return data

    def clean_start_date(self):
        cleaned_data = super(NewProjectForm, self).clean()

        data = cleaned_data.get('start_date')

        if datetime.datetime.today().strftime('%d/%m/%Y') > data.strftime('%d/%m/%Y'):
            raise forms.ValidationError('Escolha uma data válida')

        return data

    def clean_forecast_finish_date(self):
        cleaned_data = super(NewProjectForm, self).clean()

        data = cleaned_data.get('forecast_finish_date')

        if cleaned_data.get('start_date').strftime('%d/%m/%Y') > data.strftime('%d/%m/%Y'):
            raise forms.ValidationError(
                'A previsão de término não pode ser menor que a data de início do projeto.')

        return data


class UpdateProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['description', 'manager', 'leader', 'start_date',
                  'forecast_finish_date', 'budget', 'rating']
        labels = {
            'name': ('Nome'),
            'description': ('Descrição'),
            'manager': ('Gerente'),
            'leader': ('Líder do Projeto'),
            'start_date': ('Data de Início'),
            'forecast_finish_date': ('Previsão de Término'),
            'budget': ('Orçamento'),
            'rating': ('Classificação')
        }

    
    def clean_start_date(self):
        cleaned_data = super(UpdateProjectForm, self).clean()

        data = cleaned_data.get('start_date')

        if datetime.datetime.today().strftime('%d/%m/%Y') > data.strftime('%d/%m/%Y'):
            raise forms.ValidationError('Escolha uma data válida')

        return data

    def clean_forecast_finish_date(self):
        cleaned_data = super(UpdateProjectForm, self).clean()

        data = cleaned_data.get('forecast_finish_date')

        if cleaned_data.get('start_date').strftime('%d/%m/%Y') > data.strftime('%d/%m/%Y'):
            raise forms.ValidationError(
                'A previsão de término não pode ser menor que a data de início do projeto.')

        return data


class NewProjectMemberForm(forms.ModelForm):

    class Meta:

        model = ProjectTeam
        fields = ['name']
        labels = {
            'name': ('Nome'),
        }


class ConnectProjectIndicatorForm(forms.ModelForm):

    class Meta:

        model = ProjectIndicator
        fields = ['indicator', 'max_value', 'min_value']
        labels = {
            'indicator': ('Indicador'),
            'max_value': ('Valor Máximo'),
            'min_value': ('Valor Mínimo'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['indicator'].queryset = Indicator.objects.filter(
            is_active=True).order_by('name')

    def clean(self):
        cleaned_data = super(ConnectProjectIndicatorForm, self).clean()

        max_value = cleaned_data.get('max_value')
        min_value = cleaned_data.get('min_value')

        if min_value > max_value:
            raise forms.ValidationError(
                'Valor Mínimo não pode superar o Máximo.')

    #TODO Validar se o indicador já existe


class MonitorProjectIndicatorForm(forms.ModelForm):

    class Meta:

        model = ProjectIndicatorMonitor
        fields = ['value']
        labels = {
            'value': ('Valor'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewProjectActivityForm(forms.ModelForm):

    class Meta:

        model = Activity
        fields = ['name', 'description', 'budget']
        labels = {
            'name': ('Nome'),
            'description': ('Descrição'),
            'budget': ('Orçamento'),
        }


class ProjectCancelForm(forms.ModelForm):

    class Meta:

        model = ProjectStatusMonitor
        fields = ['description']
        labels = {
            'description': ('Justificativa'),
        }


class NewProjectFollowUpForm(forms.ModelForm):

    class Meta:

        model = ProjectFollowUp
        fields = ['description']
        labels = {
            'description': ('Acompanhamento'),
        }

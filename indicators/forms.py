from django import forms
from django.contrib.auth.models import User

from .models import Indicator


class NewIndicatorForm(forms.ModelForm):
    #Formulário de cadastro de um novo indicador
    class Meta:
        model = Indicator
        fields = ['name',]
        labels = { 'name': ('Nome'), }

    
    def clean_name(self):
        cleaned_data = super(NewIndicatorForm, self).clean()

        data = cleaned_data.get('name')

        n = Indicator.objects.filter(name=data)

        if n.exists():
            raise forms.ValidationError('Este nome já está sendo usado.')

        return data


class UpdateIndicatorForm(forms.ModelForm):

    class Meta:
        model = Indicator
        fields = ['name',]
        labels = { 'name': ('Nome'), }

    def clean_name(self):
        cleaned_data = super(UpdateIndicatorForm, self).clean()

        data = cleaned_data.get('name')

        n = Indicator.objects.filter(name=data)

        if n.exists():
            raise forms.ValidationError('Este nome já está sendo usado.')

        return data
from django import forms
from django.contrib.auth.models import User

from .models import Indicator


class NewIndicatorForm(forms.ModelForm):
    #Formulário de cadastro de um novo indicador
    class Meta:
        model = Indicator
        fields = ['name',]
        labels = { 'name': ('Nome'), }

    
    def clean(self):
        cleaned_data = super(NewIndicatorForm, self).clean()

        name = cleaned_data.get('name')

        n = Indicator.objects.filter(name=name)

        if n.exists:
            raise forms.ValidationError('Este nome já está sendo usado.')

class UpdateIndicatorForm(forms.ModelForm):

    class Meta:
        model = Indicator
        fields = ['name',]
        labels = { 'name': ('Nome'), }

    def clean(self):
        cleaned_data = super(NewIndicatorForm, self).clean()

        name = cleaned_data.get('name')

        n = Indicator.objects.filter(name=name)

        if n.exists:
            raise forms.ValidationError('Este nome já está sendo usado.')
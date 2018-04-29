import datetime
from django import forms
from projects.models import Project


class ReportProjectByIndicatorForm(forms.Form):

    all_active = forms.BooleanField(label='Todos os Projetos ativos', required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label='Projeto Específico', required=False)

    def clean(self):
        cleaned_data = super(ReportProjectByIndicatorForm, self).clean()

        all_active = cleaned_data.get('all_active')
        project = cleaned_data.get('project')

        if (all_active == False and project == None
            or all_active == True and project != None):
            raise forms.ValidationError('Você deve escolher uma única opção.')


class ReportProjectByStatusForm(forms.Form):

    initial_date = forms.DateField(label='Data inicial')
    final_date = forms.DateField(label='Data final')


class ReportProjectByPhaseForm(forms.Form):

    project = forms.ModelChoiceField(queryset=Project.objects.all(), label='Projeto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Project.objects.all()
        self.fields['project'].queryset = qs.active().order_by('name')
        
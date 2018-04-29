from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (ListView, DetailView)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import (LoginRequiredMixin,)
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects import models as project_models
from indicators import models as indicator_models
from .forms import ReportProjectByIndicatorForm, ReportProjectByStatusForm, ReportProjectByPhaseForm

# Create your views here.


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@login_required
def index(request):
    return render(request, 'reports/index.html')


@login_required
def report_project_by_indicator(request):

    if request.method == 'POST':
        form = ReportProjectByIndicatorForm(request.POST)
        if form.is_valid():

            if form.cleaned_data.get('all_active'):
                project_list = project_models.Project.objects.all()
                result = project_list.active()

            else:
                result = project_models.Project.objects.filter(
                    pk=form.cleaned_data.get('project').pk)

            if not result:
                messages.error(request, 'Nenhum resultado encontrado.')
                return redirect(reverse('report:by_indicator'))

            return render(request, 'reports/includes/indicator_result.html', {'result': result})
    else:
        form = ReportProjectByIndicatorForm()

    return render(request, 'reports/by_indicator.html', {'form': form})


@login_required
def report_project_by_status(request):

    if request.method == 'POST':

        form = ReportProjectByStatusForm(request.POST)

        if form.is_valid():
            initial_date = form.cleaned_data.get('initial_date')
            final_date = form.cleaned_data.get('final_date')
            result = project_models.ProjectStatusMonitor.objects.filter(status=8, created__range={initial_date, final_date})

            if not result:
                messages.error(request, 'Nenhum resultado encontrado.')
                return redirect(reverse('report:by_status'))

            return render(request, 'reports/includes/status_result.html', {'result': result})
            
    else:
        form = ReportProjectByStatusForm()

    return render(request, 'reports/by_status.html', {'form':form})


@login_required
def report_project_by_phase(request):

    if request.method == 'POST':

        form = ReportProjectByPhaseForm(request.POST)

        if form.is_valid():

            result = project_models.ProjectIndicatorMonitor.objects.filter(project=form.cleaned_data.get('project'))
            project_indicators =  project_models.ProjectIndicator.objects.filter(project=form.cleaned_data.get('project'))
            phases = project_models.ProjectIndicatorMonitor.PHASE_CHOICES

            if not result:
                messages.error(request, 'Nenhum resultado encontrado.')
                return redirect(reverse('report:by_phase'))

            return render(request, 'reports/includes/project_result.html', {'result': result, 'indicator_list':project_indicators, 'phases':phases})
            
    else:
        form = ReportProjectByPhaseForm()

    return render(request, 'reports/by_phase.html', {'form':form})

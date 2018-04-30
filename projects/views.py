from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, DetailView, UpdateView, DeleteView,)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import (LoginRequiredMixin,)
from django.contrib.auth.models import Group
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import datetime
from dateutil.relativedelta import relativedelta


from . import models, forms
from activities.models import Activity


# Create your views here.


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


class ProjectListView(LoginRequiredMixin, ListView):

    model = models.Project
    template_name = 'projects/project_list.html'
    context_object_name = 'project_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().active()


class ProjectDetailView(LoginRequiredMixin, DetailView):

    model = models.Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def dispatch(self, request, **kwargs):
        project = self.get_object()

        if in_list(project.status, '7,8'):
            return super().dispatch(request, kwargs)

        #O sistema deve exigir que, para projetos de alto risco,
        # seja registrado o acompanhamento semanal do projeto

        if project.rating == 3 and has_group(request.user, 'project_manager'):

            #Primeiro acompanhamento so inicia a partir da start_date do projeto
            if (datetime.datetime.today().strftime('%d/%m/%Y') >= project.start_date.strftime('%d/%m/%Y')
                    and not project.follow_ups.exists()):
                return redirect(reverse('project:add_follow_up', kwargs={'pk': project.pk}))
            else:

                #pega o acompanhamento mais recente
                latest_followup = project.follow_ups.order_by('-created')[0]

                #data do ultimo acompanhamento + 7
                follow_up_day = latest_followup.created + \
                    relativedelta(days=+7)

                #busca se tem acompanhamento no dia que e pra ter acompanhamento
                check_followup = models.ProjectFollowUp.objects.filter(
                    created=follow_up_day, project=project)

                #Hoje e dia de acompanhamento e nao teve acompanhamento?
                if (datetime.datetime.today().strftime('%d/%m/%Y') == follow_up_day.strftime('%d/%m/%Y')
                        and not check_followup.exists()):
                    return redirect(reverse('project:add_follow_up', kwargs={'pk': project.pk}))
                #Nao acompanhamento no dia correto e passou da data
                elif (not check_followup.exists()
                      and latest_followup.created.strftime('%d/%m/%Y') < datetime.datetime.today().strftime('%d/%m/%Y') > follow_up_day.strftime('%d/%m/%Y')):
                    return redirect(reverse('project:add_follow_up', kwargs={'pk': project.pk}))

        return super().dispatch(request, kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['team_list'] = models.ProjectTeam.objects.filter(
            project=self.kwargs.get('pk'))
        context['indicator_list'] = models.ProjectIndicator.objects.filter(
            project=self.kwargs.get('pk'))
        context['activity_list'] = Activity.objects.filter(
            project=self.kwargs.get('pk'))
        context['status_list'] = models.ProjectStatusMonitor.objects.filter(
            project=self.kwargs.get('pk')).order_by('-created')
        context['follow_up_list'] = models.ProjectFollowUp.objects.filter(
            project=self.kwargs.get('pk')).order_by('-created')
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):

    model = models.Project
    success_url = '/project/'
    template_name = 'projects/project_form.html'
    form_class = forms.NewProjectForm

    def get(self, request, *args, **kwargs):

        if has_group(request.user, 'pmo_leader'):
            return super(ProjectCreateView, self).get(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Apenas o Lider do Escritório de Projetos pode cadastrar um novo Projeto.')
            return redirect(reverse('project:index'))

    def form_valid(self, form):
        messages.success(self.request, 'Projeto cadastrado com sucesso.')
        return super(ProjectCreateView, self).form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):

    model = models.Project
    form_class = forms.UpdateProjectForm
    template_name = 'projects/project_update.html'
    success_url = '/project/'

    def get(self, request, *args, **kwargs):

        project = self.get_object()

        if in_list(project.status, '6,7,8'):
            messages.error(
                    request, 'Projeto já Em Andamento / Encerrado / Cancelado.')
            return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

        if has_group(request.user, 'pmo_leader'):
            return super(ProjectUpdateView, self).get(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Apenas o Lider do Escritório de Projetos pode atualizar o projeto.')

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.status = 1
        messages.success(
            self.request, 'Projeto alterado com sucesso! O projeto retornou para análise.')
        return super(ProjectUpdateView, self).form_valid(form)


class ProjectSearchView(LoginRequiredMixin, ListView):

    model = models.Project
    context_object_name = 'project_list'
    template_name = 'projects/project_list.html'

    def get_context_data(self, *args, **kwargs):
    	context = super(ProjectSearchView, self).get_context_data(*args, **kwargs)
    	context['query'] = self.request.GET.get('q')
    	return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q')

        if query is not None:
            return models.Project.objects.search(query)
        return models.Project.objects.none()


class ProjectDeleteView(LoginRequiredMixin, DeleteView):

    model = models.Project
    template_name = 'projects/project_delete.html'
    success_url = '/project/'

    def get(self, request, *args, **kwargs):

        project = self.get_object()

        if in_list(project.status, '6,7,8'):
            messages.error(
                request, 'Projeto já Em Andamento / Encerrado / Cancelado.')
            return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

        if has_group(request.user, 'pmo_leader'):
            return super(ProjectDeleteView, self).get(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Apenas o Lider do Escritório de Projetos pode excluir o projeto.')
            return redirect(reverse('project:index'))

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Projeto excluído com sucesso.')
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)


@login_required
def project_add_followup(request, pk):

    project = get_object_or_404(models.Project, pk=pk)

    if in_list(project.status, '7,8'):
        messages.error(request, 'Projeto já Encerrado / Cancelado.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if not has_group(request.user, 'project_manager') or project.manager != request.user:
        messages.error(
            request, 'Apenas o Gerente do Projeto pode adicionar um acompanhamento ao Projeto.')
        return redirect(reverse('project:index'))

    if request.method == 'POST':
        form = forms.NewProjectFollowUpForm(request.POST)

        if form.is_valid():
            follow_up = form.save(commit=False)
            follow_up.project = project
            follow_up.user = request.user
            follow_up.save()

            messages.success(request, 'Acompanhamento cadastrado com sucesso.')
        else:
            messages.error(request, 'Falha ao cadastrar o membro do projeto.')

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))
    else:
        form = forms.NewProjectFollowUpForm()
        return render(request, 'projects/project_add_followup.html', {'form': form})

#membros


@login_required
def project_add_member(request, pk):

    project = get_object_or_404(models.Project, pk=pk)

    if in_list(project.status, '7,8'):
        messages.error(request, 'Projeto já Encerrado / Cancelado.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if not has_group(request.user, 'project_leader') or project.leader != request.user:
        messages.error(
            request, 'Apenas o Lider do Projeto pode adicionar um membro ao Projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if request.method == 'POST':
        form = forms.NewProjectMemberForm(request.POST)

        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()

            messages.success(request, 'Membro cadastrado com sucesso.')
        else:
            messages.error(request, 'Falha ao cadastrar o membro do projeto.')

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))
    else:
        form = forms.NewProjectMemberForm()
        return render(request, 'projects/project_add_member.html', {'form': form})


class ProjectMemberDeleteView(LoginRequiredMixin, DeleteView):

    model = models.ProjectTeam
    template_name = 'projects/project_member_delete.html'
    success_url = '/project/'

    def delete(self, request, *args, **kwargs):

        obj = super(ProjectMemberDeleteView, self).get_object()

        if in_list(obj.project.status, '7,8'):
            messages.error(request, 'Projeto já Encerrado / Cancelado.')
            return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

        if has_group(request.user, 'project_leader') and obj.project.leader == request.user:

            messages.success(self.request, 'Membro excluído com sucesso.')
            return super(ProjectMemberDeleteView, self).delete(request, *args, **kwargs)
        else:
            messages.warning(
                request, 'Somente o líder do projeto pode excluir o membro.')

        return redirect(reverse('project:detail', kwargs={'pk': obj.project.pk}))


#indicador
@login_required
def project_connect_indicator(request, pk):

    project = get_object_or_404(models.Project, pk=pk)
    connection = models.ProjectIndicator(project=project)

    if in_list(project.status, '6,7,8'):
        messages.error(request, 'Projeto já em andamento')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if not has_group(request.user, 'pmo_leader'):
        messages.error(
            request, 'Apenas o Lider do Escritório de Projetos pode associar um Indicador ao Projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if request.method == 'POST':
        form = forms.ConnectProjectIndicatorForm(
            request.POST, instance=connection)

        if form.is_valid():
            c = form.save(commit=False)

            if models.ProjectIndicator.objects.filter(indicator=form.cleaned_data.get('indicator'), project=project).exists():
                messages.error(
                    request, 'Indicador já está associado ao Projeto.')
            else:
                messages.success(
                    request, 'Indicador associado com sucesso.')
                form.save()
        else:
            return render(request, 'projects/project_connect_indicator.html', {'form': form})

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))
    else:

        form = forms.ConnectProjectIndicatorForm(instance=connection)
        return render(request, 'projects/project_connect_indicator.html', {'form': form})


@login_required
def project_inform_indicator(request, pk):

    project_indicator = get_object_or_404(models.ProjectIndicator, pk=pk)

    if in_list(project_indicator.project.status, '8'):
        messages.error(request, 'Projeto já Cancelado.')
        return redirect(reverse('project:detail', kwargs={'pk': project_indicator.project.pk}))

    if not has_group(request.user, 'project_manager') or request.user != project_indicator.project.manager:
        messages.error(
            request, 'Apenas o Gerente do Projeto pode informar um indicador ao projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project_indicator.project.pk}))

    if request.method == 'POST':
        form = forms.MonitorProjectIndicatorForm(request.POST)

        if form.is_valid():
            indicator_inform = form.save(commit=False)
            indicator_inform.project = project_indicator.project
            indicator_inform.indicator = project_indicator.indicator

            # em análise, análise realizada, análise aprovada, iniciado,
            if in_list(project_indicator.project.status, '1,2,3'):
                indicator_inform.phase = 1
            # planejado
            elif in_list(project_indicator.project.status, '4,5'):
                indicator_inform.phase = 2
            # em andamento
            elif project_indicator.project.status == 6:
                indicator_inform.phase = 3
            # encerrado
            elif project_indicator.project.status == 7:
                indicator_inform.phase = 4

            monitor = models.ProjectIndicatorMonitor.objects.filter(
                            project=project_indicator.project, 
                            indicator=project_indicator.indicator,
                            phase=indicator_inform.phase
                        )

            if monitor.exists():
                messages.success(request, 'Valor para este indicador já foi informado nesta fase.')
                return redirect(reverse('project:detail', kwargs={'pk': project_indicator.project.pk}))
            else:
                indicator_inform.save()
                messages.success(request, 'Valor associado com sucesso.')

        else:
            messages.error(request, 'Falha ao associar o valor ao projeto.')

        return redirect(reverse('project:detail', kwargs={'pk': project_indicator.project.pk}))
    else:
        form = forms.MonitorProjectIndicatorForm()

        return render(request, 'projects/project_inform_indicator.html', {'form': form})


#atividade
@login_required
def project_add_activity(request, pk):

    project = get_object_or_404(models.Project, pk=pk)
    activity = Activity(project=project)

    if in_list(project.status, '6,7,8'):
        messages.error(
            request, 'Projeto já Em Andamento / Encerrado / Cancelado.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if not has_group(request.user, 'project_leader') or project.leader != request.user:
        messages.error(
            request, 'Apenas o Lider do Projeto pode adicionar ima atividade ao projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if request.method == 'POST':
        form = forms.NewProjectActivityForm(request.POST, instance=activity)

        if form.is_valid():
            form.save()
            project.status = 1
            project.save()

            messages.success(request, 'Atividade cadastrada com sucesso.')
        else:
            messages.error(
                request, 'Falha ao cadastrar a atividade do projeto.')
            return render(request, 'projects/project_add_activity.html', {'form': form})

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))
    else:
        form = forms.NewProjectActivityForm(instance=activity)
        return render(request, 'projects/project_add_activity.html', {'form': form})


class ProjectActivityDeleteView(LoginRequiredMixin, DeleteView):

    model = Activity
    template_name = 'projects/project_activity_delete.html'
    success_url = '/project/'

    def get(self, request, *args, **kwargs):

        obj = super(ProjectActivityDeleteView, self).get_object()

        if in_list(obj.project.status, '6,7,8'):
            messages.error(
                request, 'Projeto já Em Andamento / Encerrado / Cancelado.')
            return redirect(reverse('project:detail', kwargs={'pk': obj.project.pk}))

        if has_group(request.user, 'project_leader'):
            return super(ProjectActivityDeleteView, self).get(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Apenas o Lider do Projetos pode excluir a atividade.')
            return redirect(reverse('project:index'))

    def delete(self, request, *args, **kwargs):
        obj = super(ProjectActivityDeleteView, self).get_object()
        obj.project.status = 1
        obj.project.save()
        return super(ProjectActivityDeleteView, self).delete(request, *args, **kwargs)

#status


@login_required
def project_change_status(request, pk):

    project = get_object_or_404(models.Project, pk=pk)

    if not has_group(request.user, 'project_manager') or project.manager != request.user:
        messages.error(
            request, 'Apenas Usuário autorizado pode alterar o status do projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if request.method == 'POST':

        status_update = models.ProjectStatusMonitor(
            project=project,
            user=request.user,
        )

        #Quando aprovar a analise do projeto
        if project.status == 2:
            status_update.description = request.POST.get('description')

        if project.status <= 6:
            project.status += 1

        #Se for encerrar o projeto, adiciona a data de encerramento real
        if project.status == 7:
            project.end_date = datetime.datetime.today()

        status_update.status = project.status

        status_update.save()
        project.save()

        messages.success(request, 'Status alterado com sucesso.')

    return redirect(reverse('project:detail', kwargs={'pk': project.pk}))


@login_required
def project_cancel(request, pk):

    project = get_object_or_404(models.Project, pk=pk)
    
    if in_list(project.status, '8'):
        messages.error(
            request, 'Projeto já Cancelado.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if not has_group(request.user, 'project_manager') or project.manager != request.user:
        messages.error(
            request, 'Apenas Usuário autorizado pode cancelar o projeto.')
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    if request.method == 'POST':
        form = forms.ProjectCancelForm(request.POST)

        if form.is_valid():
            f = form.save(commit=False)
            f.project=project
            f.user=request.user
            f.status=8
            f.save()
            project.status = 8
            project.save()
            messages.success(request, 'Projeto cancelado com sucesso.')
        else:
            messages.error(request, 'Falha ao cancelar o projeto.')

        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))
    else:
        form = forms.ProjectCancelForm()
        return render(request, 'projects/project_cancel.html', {'form': form, 'project': project})

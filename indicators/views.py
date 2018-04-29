from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, DetailView, UpdateView, DeleteView, FormView)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import (LoginRequiredMixin,)
from django.contrib.auth.models import Group
from django.contrib import messages
from django.template.loader import render_to_string

from .models import Indicator
from .forms import NewIndicatorForm, UpdateIndicatorForm

# Create your views here.


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


class IndicatorListView(LoginRequiredMixin, ListView):
    
    model = Indicator
    template_name = 'indicators/indicator_list.html'
    context_object_name = 'indicator_list'
    paginate_by = 10

    def get_queryset(self):
        return Indicator.objects.filter(is_active=True).order_by('name')


class IndicatorSearchView(LoginRequiredMixin, ListView):
    
    model = Indicator
    template_name = 'indicators/indicator_list.html'
    context_object_name = 'indicator_list'

    def get_context_data(self, *args, **kwargs):
    	context = super(IndicatorSearchView, self).get_context_data(*args, **kwargs)
    	context['query'] = self.request.GET.get('q')
    	return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q')

        if query is not None:
            return Indicator.objects.search(query)
        return Indicator.objects.none()


class IndicatorCreateView(LoginRequiredMixin, CreateView):

    model = Indicator
    success_url = '/indicator/'
    template_name = 'indicators/indicator_form.html'
    form_class = NewIndicatorForm

    def get(self, request, *args, **kwargs):

        if has_group(request.user, 'pmo_leader'):
            return super(IndicatorCreateView, self).get(request, *args, **kwargs)
        else:
            messages.error(
                request, 'Apenas o Lider do Escritório de Projetos pode cadastrar um novo Indicador.')
            return redirect(reverse('indicator:index'))

    def form_valid(self, form):
        messages.success(self.request, 'Indicador cadastrado com sucesso.')
        return super(IndicatorCreateView, self).form_valid(form)


class IndicatorUpdateView(LoginRequiredMixin, UpdateView):

    model = Indicator
    form_class = UpdateIndicatorForm
    template_name = 'indicators/indicator_update.html'
    success_url = '/indicator/'

    def get(self, request, *args, **kwargs):

        if has_group(request.user, 'pmo_leader'):
            return super(IndicatorUpdateView, self).get(request, *args, **kwargs)
        else:
            messages.error(request, 'Apenas o Lider do Escritório de Projetos pode atualizar o Indicador.')
            return redirect(reverse('indicator:index'))
    
    def form_valid(self, form):
        messages.success(self.request, 'Indicador alterado com sucesso.')
        return super(IndicatorUpdateView, self).form_valid(form)


class IndicatorDeleteView(LoginRequiredMixin, DeleteView):

    model = Indicator
    template_name = 'indicators/indicator_delete.html'
    success_url = '/indicator/'

    def get(self, request, *args, **kwargs):

        if has_group(request.user, 'pmo_leader'):
            return super(IndicatorDeleteView, self).get(request, *args, **kwargs)
        else:
            messages.error(request, 'Apenas o Lider do Escritório de Projetos pode excluir o Indicador.')
            return redirect(reverse('indicator:index'))

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Indicador excluído com sucesso.')
        return super(IndicatorDeleteView, self).delete(request, *args, **kwargs)
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^indicator$', views.report_project_by_indicator, name='by_indicator'),
    url(r'^status$', views.report_project_by_status, name='by_status'),
    url(r'^phase$', views.report_project_by_phase, name='by_phase'),
]
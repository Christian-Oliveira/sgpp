from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProjectListView.as_view(), name='index'),
    url(r'create/$', views.ProjectCreateView.as_view(), name='create'),
    url(r'(?P<pk>\d+)/detail$', views.ProjectDetailView.as_view(), name='detail'),
    url(r'(?P<pk>\d+)/update$', views.ProjectUpdateView.as_view(), name='update'),
    url(r'(?P<pk>\d+)/delete$', views.ProjectDeleteView.as_view(), name='delete'),
    url(r'^search/$', views.ProjectSearchView.as_view(), name='search'),

    url(r'(?P<pk>\d+)/add/followup$', views.project_add_followup, name='add_follow_up'),

    url(r'(?P<pk>\d+)/add/member$', views.project_add_member, name='add_member'),
    url(r'(?P<pk>\d+)/delete/member$', views.ProjectMemberDeleteView.as_view(), name='delete_member'),

    url(r'(?P<pk>\d+)/connect/indicator$', views.project_connect_indicator, name='connect_indicator'),
    url(r'(?P<pk>\d+)/inform/indicator$', views.project_inform_indicator, name='inform_indicator'),
    
    url(r'(?P<pk>\d+)/add/activity$', views.project_add_activity, name='add_activity'),
    url(r'(?P<pk>\d+)/delete/activity$', views.ProjectActivityDeleteView.as_view(), name='delete_activity'),

    url(r'(?P<pk>\d+)/change/status$', views.project_change_status, name='change_status'),
    url(r'(?P<pk>\d+)/cancel$', views.project_cancel, name='cancel'),
]
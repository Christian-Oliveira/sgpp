from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndicatorListView.as_view(), name='index'),
    url(r'^create/$', views.IndicatorCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update$', views.IndicatorUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete$', views.IndicatorDeleteView.as_view(), name='delete'),
    url(r'^search/$', views.IndicatorSearchView.as_view(), name='search'),
]
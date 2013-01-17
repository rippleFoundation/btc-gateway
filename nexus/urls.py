from django.conf.urls import patterns, url
from nexus import views

urlpatterns = patterns('',
    url(r'^bcin$', views.bcin, name='bcin'),
	url(r'^bcout$', views.bcout, name='bcout'),
)
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'nexus.views.index', name='index'),
	url(r'^redeem/', 'nexus.views.redeem', name='redeem'),
	#url(r'^/bcin/$', 'nexus.views.bcin', name='nexus:bcin'),
	#url(r'^bcin/', 'nexus.views.bcin', name='nexus:bcin'),

    url(r'^', include('nexus.urls', namespace='nexus')),
	
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

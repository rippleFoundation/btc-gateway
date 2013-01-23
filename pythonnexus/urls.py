from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	url(r'^$', 'pythonnexus.views.index', name='index'),
	url(r'^deposit/', 'pythonnexus.views.deposit', name='deposit'),
	url(r'^redeem/', 'pythonnexus.views.redeem', name='redeem'),
    url(r'^bcin/$', 'pythonnexus.views.bcin', name='bcin'),
	url(r'^bcout/$', 'pythonnexus.views.bcout', name='bcout'),
	#url(r'^/bcin/$', 'nexus.views.bcin', name='nexus:bcin'),
	#url(r'^bcin/', 'nexus.views.bcin', name='nexus:bcin'),

	#url(r'^', include('nexus.urls', namespace='nexus')),
	
	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)

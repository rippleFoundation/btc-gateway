from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'pythonnexus.views.index', name='index'),
	url(r'^deposit/', 'pythonnexus.views.deposit', name='deposit'),
	url(r'^redeem/', 'pythonnexus.views.redeem', name='redeem'),
    url(r'^bcin/$', 'pythonnexus.views.bcin', name='bcin'),
	url(r'^bcout/$', 'pythonnexus.views.bcout', name='bcout'),

	url(r'^admin/', include(admin.site.urls)),
)

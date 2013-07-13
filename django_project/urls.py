from django.conf.urls import patterns, include, url

from django_project import django_server

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url('^$', django_server.index, name='index'),
	url('^pages/(?P<location>.+)', django_server.page, name='pages'),
	url('^event', django_server.event, name='event'),
	url('^rsc', django_server.rsc, name='resource'),
	# Examples:
	# url(r'^$', 'django_project.views.home', name='home'),
	# url(r'^django_project/', include('django_project.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
)

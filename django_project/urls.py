from django.conf.urls import patterns, include, url

from django_project import django_server

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
	url('^$', django_server.index, name='index'),
	url('^pages/(?P<location>.+)', django_server.page, name='pages'),
	url('^event/(?P<view_id>[^/]+)', django_server.event, name='event'),
	url('^form/(?P<view_id>[^/]+)', django_server.form, name='form'),
	url('^rsc/(?P<view_id>[^/]+)/(?P<rsc_id>[^/]+)', django_server.rsc, name='resource'),

	url('^accounts/login', django_server.login_form, name='login'),
	url('^accounts/process_login', django_server.process_login, name='process_login'),
	# Examples:
	# url(r'^$', 'django_project.views.home', name='home'),
	# url(r'^django_project/', include('django_project.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
)


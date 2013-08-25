from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django_app

admin.autodiscover()
urlpatterns = patterns('',
	url('^$', django_app.login_form, name='login'),
	url('^pages$', django_app.root_page, name='root page'),
	url('^pages/(?P<location>.*)', django_app.page, name='pages'),
	url('^event/(?P<view_id>[^/]+)', django_app.event, name='event'),
	url('^form/(?P<view_id>[^/]+)', django_app.form, name='form'),
	url('^rsc/(?P<view_id>[^/]+)/(?P<rsc_id>[^/]+)', django_app.rsc, name='resource'),

	url('^accounts/login', django_app.login_form, name='login'),
	url('^accounts/process_login', django_app.process_login, name='process_login'),
	url('^accounts/logout', django_app.account_logout, name='logout'),
	# Examples:
	# url(r'^$', 'django_app.views.home', name='home'),
	# url(r'^django_app/', include('django_app.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)


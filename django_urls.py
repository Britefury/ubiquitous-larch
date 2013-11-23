from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django_app

admin.autodiscover()

if django_app.USE_SIMPLE_AND_INSECURE_LOGIN:
	_index_url = url('^$', django_app.login_form, name='login')
else:
	_index_url = url('^$', django_app.index, name='index')


urlpatterns = patterns('',
	url('^$', django_app.index, name='index'),
	#url('^$', django_app.login_form, name='login'),
	url('^pages/(?P<category>[^/]+)/(?P<name>[^/]+)/(?P<location>.*)', django_app.page, name='pages'),
	url('^pages/(?P<category>[^/]+)/(?P<name>[^/]+)', django_app.front_page, name='frpnt page'),
	url('^pages[/]?$', django_app.root_page, name='root page'),
	url('^event/(?P<category>[^/]+)/(?P<name>[^/]+)/(?P<view_id>[^/]+)', django_app.event, name='event'),
	url('^form/(?P<category>[^/]+)/(?P<name>[^/]+)/(?P<view_id>[^/]+)', django_app.form, name='form'),
	url('^rsc/(?P<category>[^/]+)/(?P<name>[^/]+)/(?P<view_id>[^/]+)/(?P<rsc_id>[^/]+)', django_app.rsc, name='resource'),

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


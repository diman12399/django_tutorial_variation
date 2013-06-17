# -*- encoding:utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'django_tutorial_variation.views.home',
                       #     name='home'),
                       # url(r'^django_tutorial_variation/',
                       #     include('django_tutorial_variation.foo.urls')),

                       # Uncomment the admin/doc line below to
                       # enable admin documentation:
                       # url(r'^admin/doc/',
                       #     include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^polls/',
                           include('polls.urls', namespace='polls')),
                       url(r'^admin/',
                           include(admin.site.urls)),
                       url(r'^static/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT}),
                       )

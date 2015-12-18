from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from branches.views import *
from branches.api import *


v1_api = Api(api_name='v1')
v1_api.register(ServerResource())
v1_api.register(ProjectResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^servers/$', ServerListView.as_view(), name='server-list'),
    url(r'^servers/new/$', NewServerView.as_view(), name='new-server'),
    url(r'^server/(?P<pk>\d+)/$', ServerDetailView.as_view(), name='server-detail'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^api/', include(v1_api.urls)),
)

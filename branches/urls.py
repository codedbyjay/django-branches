from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from branches.views import *
from branches.api import *

v1_api = Api(api_name='v1')
v1_api.register(ServerResource())
v1_api.register(ProjectResource())
v1_api.register(RequestResource())

urlpatterns = patterns('',

    # projects
    url(r'^$', ProjectListView.as_view(), name='project-list'),
    url(r'^(?P<owner>[\w\-_]+)/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/new/$', NewProjectView.as_view(), name='new-project'),
    url(r'^(?P<owner>[\w\-_]+)/(?P<project_slug>[\w\-_]+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^(?P<owner>[\w\-_]+)/(?P<project_slug>[\w\-_]+)/edit/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^(?P<owner>[\w\-_]+)/(?P<project_slug>[\w\-_]+)/delete/$', ProjectDeleteView.as_view(), name='project-delete'),


    # Servers
    # url(r'^servers/$', ServerListView.as_view(), name='server-list'),
    # url(r'^servers/new/$', NewServerView.as_view(), name='new-server'),
    # url(r'^server/(?P<pk>\d+)/$', ServerDetailView.as_view(), name='server-detail'),
    # url(r'^server/(?P<pk>\d+)/edit/$', ServerUpdateView.as_view(), name='server-edit'),
    # url(r'^server/(?P<pk>\d+)/delete/$', ServerDeleteView.as_view(), name='server-delete'),
    # url(r'^server/(?P<pk>\d+)/initialize/$', InitializeServerView.as_view(), name='initialize-server'),
    # url(r'^server/(?P<pk>\d+)/initializing/$', ServerInitiailizingView.as_view(), name='server-initializing'),
    # url(r'^server/(?P<pk>\d+)/log/$', ServerLogView.as_view(), name='server-log'),

    # # repositories
    # url(r'^repositories/$', RepositoryListView.as_view(), name='repository-list'),
    # url(r'^repositories/new/$', NewRepositoryView.as_view(), name='new-repository'),

    # # integrations
    # url(r'^rackspace/connect/$', RackspaceConnectView.as_view(), name='rackspace-connect'),
    # url(r'^rackspace/servers/$', RackspaceServerListView.as_view(), name='rackspace-server-list'),

    # url(r'^digitalocean/connect/$', DigitalOceanConnectView.as_view(), name='digitalocean-connect'),
    # url(r'^digitalocean/authorize/$', DigitalOceanAuthorizeView.as_view(), name='digitalocean-authorize'),
    # url(r'^digitalocean/servers/$', DigitalOceanServerListView.as_view(), name='digitalocean-server-list'),

    # API
    url(r'^api/', include(v1_api.urls)),
)

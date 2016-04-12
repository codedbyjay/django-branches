from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from branches.views import *
from branches.api import *

v1_api = Api(api_name='v1')
v1_api.register(ServerResource())
v1_api.register(ProjectResource())
v1_api.register(ChangeBranchRequestResource())

urlpatterns = patterns('',
    # Servers
    url(r'^servers/$', ServerListView.as_view(), name='server-list'),
    url(r'^servers/new/$', NewServerView.as_view(), name='new-server'),
    url(r'^server/(?P<pk>\d+)/$', ServerDetailView.as_view(), name='server-detail'),
    url(r'^server/(?P<pk>\d+)/edit/$', ServerUpdateView.as_view(), name='server-edit'),
    url(r'^server/(?P<pk>\d+)/delete/$', ServerDeleteView.as_view(), name='server-delete'),
    url(r'^server/(?P<pk>\d+)/initialize/$', InitializeServerView.as_view(), name='initialize-server'),
    url(r'^server/(?P<pk>\d+)/initializing/$', ServerInitiailizingView.as_view(), name='server-initializing'),
    url(r'^server/(?P<pk>\d+)/log/$', ServerLogView.as_view(), name='server-log'),

    # repositories
    url(r'^repositories/$', RepositoryListView.as_view(), name='repository-list'),
    url(r'^repositories/new/$', NewRepositoryView.as_view(), name='new-repository'),

    # projects
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^project/(?P<pk>\d+)/edit/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^project/(?P<pk>\d+)/delete/$', ProjectDeleteView.as_view(), name='project-delete'),
    url(r'^server/(?P<pk>\d+)/new-project/$', NewProjectView.as_view(), name='new-project'),

    # API
    url(r'^api/', include(v1_api.urls)),
)

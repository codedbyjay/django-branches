import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf.urls import patterns, include, url

from tastypie.resources import ModelResource

from branches.models import *

class ServerResource(ModelResource):
    class Meta:
        queryset = Server.objects.all()
        resource_name = "server"

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/current-branch/$" % self._meta.resource_name, self.wrap_view('get_current_branch'), name="current-branch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/branches/$" % self._meta.resource_name, self.wrap_view('get_branches'), name="branches"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/change-branch/$" % self._meta.resource_name, self.wrap_view('change_branch'), name="change-branch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/log/$" % self._meta.resource_name, self.wrap_view('log'), name="log"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/status/$" % self._meta.resource_name, self.wrap_view('get_status'), name="get-status"),
        ]

    def get_current_branch(self, request, **kwargs):
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        response = json.dumps(dict(branch=project.current_branch))
        return HttpResponse(response, content_type="application/json")

    def get_branches(self, request, **kwargs):
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        response = json.dumps(project.available_branches)
        return HttpResponse(response, content_type="application/json")

    def change_branch(self, request, **kwargs):
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        new_branch = request.POST.get("branch")
        project.request_branch_change(new_branch)
        response = json.dumps(dict(message="Changing branch"))
        return HttpResponse(response, content_type="application/json")

    def log(self, request, **kwargs):
        limit = request.GET.get("limit", 50)
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        log = project.get_log(limit=limit)
        return HttpResponse(log)

    def get_commits(self, request, **kwargs):
        limit = request.GET.get("limit", 50)
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        commits = project.get_commits(limit=limit)
        response = json.dumps(dict(commits=commits))
        return HttpResponse(response, content_type="application/json")

    def get_status(self, request, **kwargs):
        print("I got as far as here...")
        limit = request.GET.get("limit", 50)
        pk = kwargs.get("pk")
        project = get_object_or_404(Project, pk=pk)
        info = project.get_status(limit=limit)
        response = json.dumps(dict(info=info))
        return HttpResponse(response, content_type="application/json")

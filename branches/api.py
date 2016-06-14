import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf.urls import patterns, include, url

from tastypie.resources import ModelResource
from tastypie import fields

from branches.models import *

class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"

class ServerResource(ModelResource):
    class Meta:
        queryset = Server.objects.all()
        resource_name = "server"

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/current-branch/$" % self._meta.resource_name, self.wrap_view('get_current_branch'), name="current-branch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/branches/$" % self._meta.resource_name, self.wrap_view('get_branches'), name="branches"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/change-branch/$" % self._meta.resource_name, self.wrap_view('change_branch'), name="change-branch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/update-branch-list/$" % self._meta.resource_name, self.wrap_view('update_branch_list'), name="update-branch-list"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/cancel-change-branch/$" % self._meta.resource_name, self.wrap_view('cancel_change_branch'), name="cancel-change-branch"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/log/$" % self._meta.resource_name, self.wrap_view('log'), name="log"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/status/$" % self._meta.resource_name, self.wrap_view('get_status'), name="get-status"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/change-branch-log/$" % self._meta.resource_name, self.wrap_view('log'), name="get-change-branch-log"),
        ]

    def get_current_branch(self, request, **kwargs):
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        response = json.dumps(dict(branch=project.current_branch))
        return HttpResponse(response, content_type="application/json")

    def update_branch_list(self, request, **kwargs):
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        branches = project.update_branch_list()
        return JsonResponse(dict(message="Updated branch list", result=True, 
            branches=branches))

    def get_branches(self, request, **kwargs):
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        response = json.dumps(project.available_branches)
        return HttpResponse(response, content_type="application/json")

    def change_branch(self, request, **kwargs):
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        new_branch = request.POST.get("branch")
        if not new_branch:
            return JsonResponse(dict(result=False, message="Please supply a branch"))
        change_branch_request = project.request_branch_change(new_branch)
        return JsonResponse(dict(message="Changing branch", result=True, 
            change_branch_request_pk=change_branch_request.pk))

    def cancel_change_branch(self, request, **kwargs):
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        last_change_branch_request = project.last_change_branch_request
        if last_change_branch_request.complete or last_change_branch_request.cancelled:
            return JsonResponse(dict(result=False, message="No branch change in progress, nothing to change"))
        result = project.cancel_change_branch()
        if result:
            return JsonResponse(dict(result=True, message="Successfully cancelled your branch change"))
        return JsonResponse(dict(result=result, message="Something went wrong, we couldn't cancel... try again?"))

    def log(self, request, **kwargs):
        limit = request.GET.get("limit", 7)
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        log = project.get_log(limit=limit)
        response = json.dumps(dict(log=log, 
            is_changing_branch=project.is_changing_branch,
            is_change_branch_requested=project.is_change_branch_requested))
        return HttpResponse(response, content_type="application/json")

    def get_commits(self, request, **kwargs):
        limit = request.GET.get("limit", 50)
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        commits = project.get_commits(limit=limit)
        response = json.dumps(dict(commits=commits))
        return HttpResponse(response, content_type="application/json")

    def get_status(self, request, **kwargs):
        print("I got as far as here...")
        limit = request.GET.get("limit", 50)
        pk = kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        info = project.get_status(limit=limit)
        last_change_branch_request = project.last_change_branch_request
        if last_change_branch_request:
            resource = RequestResource()
            resource_bundle = resource.build_bundle(obj=last_change_branch_request, request=request)
            bundle_json = resource.serialize(None, resource.full_dehydrate(resource_bundle), 'application/json')
            info["last_change_branch_request"] = json.loads(bundle_json)
        else:
            info["last_change_branch_request"] = {}
        response = json.dumps(dict(info=info))
        return HttpResponse(response, content_type="application/json")



class RequestResource(ModelResource):
    class Meta:
        queryset = Request.objects.all()
        resource_name = "change-branch-request"

    def dehydrate(self, bundle):
        obj = bundle.obj
        bundle.data["complete"] = obj.complete
        bundle.data["in_progress"] = obj.in_progress
        bundle.data["cancelled"] = obj.cancelled
        bundle.data["requested"] = obj.requested
        change_branch_log = bundle.obj.change_branch_log
        if change_branch_log:
            bundle.data["log"] = change_branch_log.get_log(limit=15)
        return bundle

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/log/$" % self._meta.resource_name, self.wrap_view('log'), name="log"),
        ]

    def log(self, request, pk, **kwargs):
        change_branch_request = get_object_or_404(Request, pk=pk)
        return HttpResponse(change_branch_request.change_branch_log.get_log(limit=1000))

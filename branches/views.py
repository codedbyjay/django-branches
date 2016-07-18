from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings

import pyrax
from requests_oauthlib import OAuth2Session
import digitalocean

from .models import Server, Repository, copy_key_to_server, Project, UserProfile
from .forms import (
    NewServerForm, InitializeServerForm, NewProjectForm, NewRepositoryForm, 
    RackspaceConnectForm
)

class ServerListView(ListView):
    """ Lists all the servers the user has
    """ 

    model = Server

class RepositoryListView(ListView):

    model = Repository


class NewRepositoryView(CreateView):
    """ View for creating a new server
    """

    model = Repository
    form_class = NewRepositoryForm

    def get_success_url(self):
        return reverse("branches:repository-list")

class NewServerView(CreateView):
    """ View for creating a new server
    """

    model = Server
    form_class = NewServerForm

    def get_success_url(self):
        server = self.object
        project = server.project
        owner = project.owner.username
        return reverse(
            "branches:initialize-server", 
            kwargs=dict(
                server=server.slug, 
                project=project.slug,
                owner=owner))

    def get_form_kwargs(self):
        kwargs = super(NewServerView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_invalid(self, form):
        print("Errors in form")
        print(form.errors)
        return super(NewServerView, self).form_invalid(form)

    def form_valid(self, form):
        print("Processing form...")
        cleaned_data = form.cleaned_data
        project = cleaned_data.pop("project")
        owner = cleaned_data.pop("owner")
        location = cleaned_data.pop("location")
        server = form.save(commit=False)
        server.project = project
        server.owner = owner
        server.save()
        if not server.repository:
            server.repository = Repository.objects.create(location=location)
            server.save()
        else:
            repository = server.repository
            repository.location = location
            repository.save()
        self.object = server
        return redirect(self.get_success_url())


class ServerUpdateView(UpdateView):
    model = Server
    form_class = NewServerForm
    template_name = "branches/server_form.html"

class ServerDeleteView(DeleteView):
    model = Server
    template_name = "branches/server_delete.html"

    def get_success_url(self):
        return reverse("branches:server-list")

class InitializeServerView(FormView, SingleObjectMixin):

    model = Server
    form_class = InitializeServerForm
    template_name = "branches/initialize_server.html"

    def __init__(self, *args, **kwargs):
        self.object = None
        super(InitializeServerView, self).__init__(*args, **kwargs)

    def get_form(self):
        server = self.get_object()
        form = self.form_class(server, self.request.POST or None, 
            initial=self.get_initial(),
            instance=server)
        return form

    def get_success_url(self):
        return reverse("branches:server-log", kwargs=dict(pk=self.get_object().pk))

    def get_initial(self):
        server = self.get_object()
        return {
            "address" : server.address,
            "port" : server.port,
        }

    def form_valid(self, form):
        server = form.save()
        # Get the uername and password and try to connect
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        server.initialize(username, password)
        return redirect("branches:server-initializing", pk=server.pk)

class ServerInitiailizingView(DetailView):
    model = Server
    template_name = "branches/initializing_server.html"

    def get(self, *args, **kwargs):
        server = self.get_object()
        if server.initialized:
            return redirect("branches:server-detail", pk=server.pk)
        return super(ServerInitiailizingView, self).get(*args, **kwargs)

class ServerDetailView(DetailView):

    model = Server
    context_object_name = "server"

class ServerLogView(DetailView):

    model = Server
    context_object_name = "server"
    template_name = "branches/server_log.html"

class ProjectListView(ListView):

    model = Project
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super(ProjectListView, self).get_context_data(**kwargs)
        ctx["page"] = "project-list"
        return ctx


class ProjectDetailView(DetailView):

    model = Project
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "project_slug"

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = NewProjectForm

    def get_success_url(self):
        return reverse("branches:project-detail", kwargs=dict(pk=self.get_object().pk))

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = "branches/project_delete.html"

class NewProjectView(CreateView):

    model = Project
    form_class = NewProjectForm

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(NewProjectView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
        

class RackspaceConnectView(FormView):

    form_class = RackspaceConnectForm
    template_name = "branches/rackspace_connect.html"    

    def get(self, request, *args, **kwargs):
        profile = UserProfile.get_profile(self.request.user)
        if profile.rackspace_username and profile.rackspace_api_key:
            return redirect("branches:rackspace-server-list")
        return super(RackspaceConnectView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        api_key = cleaned_data.get("api_key")
        username = cleaned_data.get("username")
        profile = UserProfile.get_profile(self.request.user)
        profile.rackspace_username = username
        profile.rackspace_api_key = api_key
        profile.save()
        return redirect("branches:rackspace-server-list")


class RackspaceServerListView(ListView):

    context_object_name = "servers"
    template_name = "branches/rackspace_server_list.html"

    def get_queryset(self):
        pyrax.set_setting("identity_type", "rackspace")
        profile = UserProfile.get_profile(self.request.user)
        username = profile.rackspace_username
        api_key = profile.rackspace_api_key
        pyrax.set_credentials(username, api_key)
        return pyrax.cloudservers.list()

    def post(self, request, *args, **kwargs):
        data = request.POST
        server_ids = data.getlist("server")
        servers = [server for server in self.get_queryset() if server.id in server_ids]
        for server in servers:
            address = server.networks.get("public")[0]
            Server.objects.create(name=server.name, address=address)
        return redirect("branches:server-list")



class DigitalOceanConnectView(RedirectView):

    def get_oauth(self):
        client_id = settings.DIGITAL_OCEAN_CLIENT_ID
        client_secret = settings.DIGITAL_OCEAN_CLIENT_SECRET
        redirect_uri = "%s%s" % (
            settings.SITE_URL, reverse("branches:digitalocean-authorize"))
        scope = ["read"]
        oauth = OAuth2Session(
            client_id, 
            redirect_uri=redirect_uri,
            scope=scope)        
        return oauth

    def get_redirect_url(self, *args, **kwargs):
        url = "https://cloud.digitalocean.com/v1/oauth/authorize"
        oauth = self.get_oauth()
        authorization_url, state = oauth.authorization_url(
            url)
        print("Authorization url is: %s" % authorization_url)
        return authorization_url

class DigitalOceanAuthorizeView(DigitalOceanConnectView):

    def get_redirect_url(self, *args, **kwargs):
        print(self.request.GET)
        data = self.request.GET
        code = data.get("code")
        oauth = self.get_oauth()
        callback = "%s%s" % (settings.SITE_URL, self.request.path)
        token = oauth.fetch_token(
            "https://cloud.digitalocean.com/v1/oauth/token",
            code=code,
            client_secret=settings.DIGITAL_OCEAN_CLIENT_SECRET)
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        expires_at = datetime.fromtimestamp(int(token.get("expires_at")))
        profile = UserProfile.get_profile(self.request.user)
        profile.digitalocean_access_token = access_token
        profile.digitalocean_refresh_token = refresh_token
        profile.digitalocean_access_token_expiry = expires_at
        profile.save()
        return reverse("branches:digitalocean-server-list")

class DigitalOceanServerListView(ListView):

    context_object_name = "servers"
    template_name = "branches/rackspace_server_list.html"

    def get_queryset(self):
        profile = UserProfile.get_profile(self.request.user)
        manager = digitalocean.Manager(token=profile.digitalocean_access_token)
        servers = []
        for droplet in manager.get_all_droplets():
            print("Examining this droplet: %s" % droplet)
            name = droplet.name
            servers.append(Server(name=name))
        return servers



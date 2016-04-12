from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.views.generic.detail import SingleObjectMixin

from .models import Server, Repository, copy_key_to_server, Project
from .forms import (
    NewServerForm, InitializeServerForm, NewProjectForm, NewRepositoryForm
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
        pk = self.object.pk
        return reverse("branches:initialize-server", kwargs=dict(pk=pk))

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

class ProjectDetailView(DetailView):

    model = Project
    context_object_name = "project"

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

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        server = get_object_or_404(Server, pk=pk)
        self.server = server
        instance = form.save(commit=False)
        instance.server = server
        instance.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("branches:server-detail", kwargs=dict(pk=self.server.pk))

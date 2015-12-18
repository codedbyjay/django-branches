from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.http import HttpResponse

import django_rq
from socketio.namespace import BaseNamespace
from socketio import socketio_manage

from .models import Server, Repository, copy_key_to_server, Project
from .forms import NewServerForm

class ServerListView(ListView):
    """ Lists all the servers the user has
    """ 

    model = Server

class NewServerView(CreateView):
    """ View for creating a new server
    """

    model = Server
    form_class = NewServerForm

    def form_valid(self, form):
    	# Get the uername and password and try to connect
    	username = form.cleaned_data.get("username")
    	password = form.cleaned_data.get("password")
        server = self.get_object()
        server.initialize(username, password)
    	return super(NewServerView, self).form_valid(form)

class ServerDetailView(DetailView):

	model = Server
	context_object_name = "server"


class ProjectDetailView(DetailView):

    model = Project
    context_object_name = "project"


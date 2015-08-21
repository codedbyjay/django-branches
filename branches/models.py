from django.core.urlresolvers import reverse

from contextlib import contextmanager

from fabric.api import env, run, execute, cd
from fabric.contrib.files import append
from redis import Redis
import django_rq
from git import Repo

from django.db import models

from branches import *
from branches.tasks import *
from branches.networking import *


class Server(models.Model):

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    port = models.PositiveIntegerField(default=22)
    repositories = models.ManyToManyField("Repository", blank=True,  
        through="Project")
    intialized = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def initialize(self, username, password):
        """ Copy up the server's key to this server
        """
        django_rq.enqueue(copy_key_to_server, self.pk,
            username=username, password=password, port=self.port)

    def get_absolute_url(self):
        return reverse("branches:server-detail", kwargs=dict(pk=self.pk))


class Repository(models.Model):

    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    """ Links up a server to a project
    """

    server = models.ForeignKey("Server", related_name="projects")
    repository =  models.ForeignKey("Repository", related_name="projects")
    location = models.CharField(max_length=255)

    @property
    def repo(self):
        """ Return a repository object, only for use when connected to a server
        """
        return Repo(self.location)

    @property
    def current_branch(self):
        with connect(self.server):
            def get_current_branch():
                with cd(self.location):
                    return self.repo.active_branch
            result = execute(get_current_branch)
            return result.get(self.server.address)
        return None

    @property
    def available_branches(self):
        """ Returns a dictionary with available_branches and current_branch
        """
        with connect(self.server):
            def get_available_branches():
                with cd(self.location):
                    return [head.name for head in self.repo.branches]
            result = execute(get_available_branches)
            return result.get(self.server.address)
        return None

    def change_branch(self, branch):
        result = django_rq.enqueue(switch_branches, self.pk, branch)


def switch_branches(project_pk, branch):
    project = Project.objects.get(project_pk)
    server = project.server
    with connect(server):
        with cd(project.location):
            new_branch = project.repo.create_head(branch)
            project.repo.head.reference = new_branch
            project.repo.head.reset(new_branch, index=True, working_dir=True)
    result = execute(switch_branches)
    return result




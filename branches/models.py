from django.core.urlresolvers import reverse

from contextlib import contextmanager

from fabric.api import env, run, execute, cd, local
from fabric.contrib.files import append
from redis import Redis
import django_rq

from django.db import models
from django.conf import settings

from branches import *
from branches.tasks import *
from branches.networking import *
from branches.git import Repo


class Server(models.Model):

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
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
    change_branch_script = models.TextField(blank=True, null=True)

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
                    return self.repo.available_branches
            result = execute(get_available_branches)
            return result.get(self.server.address)
        return None

    def get_status(self, limit=10):
        with connect(self.server):
            def get_status():
                with cd(self.location):
                    return self.repo.get_status(limit=limit)
            result = execute(get_status)
            return result.get(self.server.address)
        return None
    

    def request_branch_change(self, branch):
        result = django_rq.enqueue(change_server_branch, self.pk, branch)

    def change_branch(self, branch):
        number_of_changes = self.change_branch_logs.count()
        script_filename = "%s/server_log_%s_%s.log" % \
            (settings.MEDIA_ROOT, self.pk, number_of_changes)
        current_branch = self.current_branch
        change_branch_log = ChangeBranchLog.objects.create(project=self,
            previous_branch=current_branch,
            current_branch=branch,
            log_filename=script_filename)
        server = self.server
        with connect(server):
            with cd(self.location):
                # Create the log file
                local("touch %s" % script_filename)
                log_file = open(script_filename, "a")
                def change_branch_task():
                    log_file.write("Changing branch from %s to %s\r\n" % \
                            (current_branch, branch))
                    log_file.write("Discarding local changes...\r\n")
                    run("git checkout -- .", stdout=log_file)
                    log_file.write("Changing branch to %s\r\n" % branch)
                    run("git checkout %s" % branch, stdout=log_file)
                    log_file.write("Running custom script\r\n")
                execute(change_branch_task)
            change_branch_log.active = False
            change_branch_log.save()
        return True

    def get_commits(self, limit=10):
        with connect(self.server):
            with cd(self.location):
                def _get_commits():
                    return self.repo.get_commits(limit=limit)
                result = execute(_get_commits)
                return result.get(self.server.address)
        return []


class ChangeBranchLog(models.Model):

    project = models.ForeignKey("Project", related_name="change_branch_logs")
    current_branch = models.CharField(max_length=255)
    previous_branch = models.CharField(max_length=255, blank=True, null=True)
    change_branch_script = models.TextField(blank=True, null=True)
    log_filename = models.FileField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def get_log(limit=50):
        """ Gets the last limit lines of the log file
        """
        result = bash("tail -n %s %s" % (limit, self.log_filename.url))
        return result

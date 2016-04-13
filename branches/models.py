from django.core.urlresolvers import reverse

from contextlib import contextmanager

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save

from fabric.api import env, run, execute, cd, local, sudo
from fabric.contrib.files import append
from redis import Redis
from bash import bash

from django_extensions.db.models import TimeStampedModel

from branches import *
from branches.tasks import *
from branches.networking import *
from branches.git import Repo
from branches.celery import get_new_task_id


class Server(TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name="servers")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(default=22)
    repositories = models.ManyToManyField(
        "Repository", blank=True,
        through="Project")
    initialized = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def initialize(self, username, password, port=None):
        """ Copy up the server's key to this server
        """
        result = copy_key_to_server.delay(
            self.pk,
            username=username, password=password, port=port or self.port)
        return result

    def get_absolute_url(self):
        return reverse("branches:server-detail", kwargs=dict(pk=self.pk))


class Repository(TimeStampedModel):

    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Project(TimeStampedModel):
    """ Links up a server to a project
    """

    server = models.ForeignKey("Server", related_name="projects")
    repository = models.ForeignKey("Repository", related_name="projects")
    location = models.CharField(max_length=255)
    change_branch_script = models.TextField(blank=True, null=True)

    def get_log(self, limit=7):
        try:
            change_branch_log = self.change_branch_logs.latest("pk")
            return change_branch_log.get_log(limit=limit)
        except ChangeBranchLog.DoesNotExist:
            return ""

    @property
    def is_changing_branch(self):
        return self.change_branch_logs.filter(active=True).exists()

    @property
    def is_change_branch_requested(self):
        return self.change_branch_requests.\
            filter(status=ChangeBranchRequest.STATUS_REQUESTED).exists()

    @property
    def change_branch_log(self):
        if self.is_changing_branch:
            change_branch_log = self.change_branch_logs.filter(active=True)[0]
            return change_branch_log.cancel()
        return False

    def cancel_change_branch(self):
        if self.last_change_branch_request:
            print("Cancelling last change branch request")
            return self.last_change_branch_request.cancel()
        print("No last change branch request, cannot cancel")
        return False

    @property
    def repo(self):
        """ Return a repository object, only for use when connected to a server
        """
        return Repo(self.location)

    @property
    def current_branch(self):
        """ Returns the branch the server is currently on
        """
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
            result = result.get(self.server.address)
            try:
                change_branch_log = self.change_branch_logs.latest("pk")
                result["change_branch_log"] = change_branch_log.get_log(limit=limit)
            except ChangeBranchLog.DoesNotExist:
                pass
            result["is_changing_branch"] = self.is_changing_branch
            result["is_change_branch_requested"] = self.is_change_branch_requested
            return result
        return None

    def request_branch_change(self, branch):
        if self.is_change_branch_requested:
            raise Exception("A branch change was already requested.")
        task_id = get_new_task_id() # generate a uuid
        change_branch_request = ChangeBranchRequest.objects.create(
            project=self,
            branch=branch,
            task_id=task_id)
        task_args = [self.pk, branch, change_branch_request.pk]
        result = change_server_branch.apply_async(args=task_args,
            task_id=task_id)
        return change_branch_request

    def change_branch(self, branch, task_id, change_branch_request_pk):
        """ This method is executed by the ``change_server_branch`` task in
            the Celery process. 
        """
        active_change_branch_logs = self.change_branch_logs.filter(active=True)
        for change_branch_log in active_change_branch_logs:
            other_task_id = change_branch_log.task_id            
            # check if this tsak is complete first
            result = change_server_branch.AsyncResult(other_task_id)
            if not result.ready():
                print("Task %s is already running, cannot change branch" % other_task_id)
                return False
            # Set this as inactive then
            change_branch_log.active = False
            change_branch_log.save()
        # Double check that none are active, in case another worker started
        if self.change_branch_logs.filter(active=True).exists():
            print("Someone beat us to it.. can't change branch")
            return False

        try:
            change_branch_request = ChangeBranchRequest.objects.get(pk=change_branch_request_pk)
            if not change_branch_request.requested:
                """ At this point we expect the request to be requested, if it's 
                    not it means that either:
                    - Some other worker has actioned the request
                    - It has been cancelled
                """
                print("Not actioning this request, it currently has status: %s" % \
                        change_branch_request.status)
                return False
            print("Request status is: %s" % change_branch_request.status)
        except ChangeBranchRequest.DoesNotExist:
            print("If this request does not exist, don't continue")
            return False
        current_branch = self.current_branch
        # Create a chnge log and mark it as active
        change_branch_log = ChangeBranchLog.objects.create(project=self,
            previous_branch=current_branch,
            current_branch=branch,
            active=True)
        change_branch_request.change_branch_log = change_branch_log
        change_branch_request.status = ChangeBranchRequest.STATUS_IN_PROGRESS
        change_branch_request.save()

        # Mark all other as inactive
        self.change_branch_logs.exclude(pk=change_branch_log.pk).\
            update(active=False)

        print("Asked to change branch from %s to %s" % (current_branch, branch))
        # Make sure the media root directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        script_filename = "%s/server_log_%s_%s.log" % \
            (settings.MEDIA_ROOT, self.pk, change_branch_log.pk)
        user_script_filename = "script_%s.sh" % change_branch_log.pk
        change_branch_log.log_filename = script_filename
        change_branch_log.save()
        server = self.server
        with connect(server):
            with cd(self.location):
                # Create the log file
                with open(script_filename, "w") as log_file:
                    def change_branch_task():
                        log_file.write("Changing branch from %s to %s\r\n" % \
                                (current_branch, branch))
                        log_file.write("Discarding local changes...\r\n")
                        run("git checkout -- .", stdout=log_file)
                        log_file.write("Changing branch to %s\r\n" % branch)
                        run("git checkout %s" % branch, stdout=log_file)
                        # check if the branch exists on origin
                        run("git pull", stdout=log_file, warn_only=True)
                        if self.change_branch_script:
                            log_file.write("Running custom script\r\n")
                            run("rm %s" % user_script_filename, warn_only=True)
                            run("touch %s" % user_script_filename)
                            append(user_script_filename, self.change_branch_script)
                            run("chmod +x %s" % user_script_filename)
                            sudo("./%s" % user_script_filename, stdout=log_file)
                    try:
                        execute(change_branch_task)
                    except Exception as e:
                        print("Exception occurred changing branches: %s" % e)
                        log_file.write(e.message)
                        change_branch_log.active = False
                        change_branch_log.save()
                        change_branch_request.status = ChangeBranchRequest.STATUS_COMPLETE
                        change_branch_request.save()
                        return False
            print("Marking task as inactive now")
            change_branch_log.active = False
            change_branch_log.save()
            change_branch_request.status = ChangeBranchRequest.STATUS_COMPLETE
            change_branch_request.save()
        return True

    def get_commits(self, limit=10):
        with connect(self.server):
            with cd(self.location):
                def _get_commits():
                    return self.repo.get_commits(limit=limit)
                result = execute(_get_commits)
                return result.get(self.server.address)
        return []

    @property
    def last_change_branch_request(self):
        try:
            return self.change_branch_requests.latest("created")
        except ChangeBranchRequest.DoesNotExist:
            return None

    def update_branch_list(self):
        with connect(self.server):
            def fetch():
                with cd(self.location):
                    self.repo.fetch()
                    return self.repo.available_branches
            result = execute(fetch)
            return result.get(self.server.address)
        return None


class ChangeBranchRequest(TimeStampedModel):

    STATUS_REQUESTED = "requested"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_COMPLETE = "complete"
    STATUS_CANCELLED = "cancelled"

    project = models.ForeignKey("Project", related_name="change_branch_requests")
    branch = models.CharField(max_length=255)
    status = models.CharField("Status", max_length=50, default=STATUS_REQUESTED)
    change_branch_log = models.OneToOneField("ChangeBranchLog", 
        blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def cancel(self):
        # Terminate the task 
        result = change_server_branch.AsyncResult(self.task_id)
        if not result.ready():
            print("Terminating the task")
            result.revoke(terminate=True)
        if self.change_branch_log:
            self.change_branch_log.active = False
            self.change_branch_log.save()
        print("Marking ourselves as cancelled")
        self.status = ChangeBranchRequest.STATUS_CANCELLED
        self.save()
        return True


    @property
    def complete(self):
        return self.status == ChangeBranchRequest.STATUS_COMPLETE

    @property
    def requested(self):
        return self.status == ChangeBranchRequest.STATUS_REQUESTED

    @property
    def cancelled(self): 
        return self.status == ChangeBranchRequest.STATUS_CANCELLED

    @property
    def in_progress(self):
        return self.status == ChangeBranchRequest.STATUS_IN_PROGRESS


class ChangeBranchLog(TimeStampedModel):

    project = models.ForeignKey("Project", related_name="change_branch_logs")
    current_branch = models.CharField(max_length=255)
    previous_branch = models.CharField(max_length=255, blank=True, null=True)
    change_branch_script = models.TextField(blank=True, null=True)
    log_filename = models.FileField(blank=True, null=True)
    active = models.BooleanField(default=True)

    @property
    def task_id(self):
        return self.change_branch_request.task_id
    

    def get_log(self, limit=50):
        """ Gets the last limit lines of the log file
        """
        result = unicode(bash("tail -n %s %s" % (limit, self.log_filename.url)))
        result = result.replace("\n", "<br>")
        result = result.replace("\r", "")
        return result


def clean_script(sender, instance, **kwargs):
    """ Remove any weird spaces from the script
    """
    print("Cleaning script")
    raw = kwargs.get("raw")
    if raw:
        return
    script = instance.change_branch_script
    if not script:
        return
    clean_line = lambda line: line.strip() + "\n"
    script = "".join(map(clean_line, script.splitlines()))
    instance.change_branch_script = script
pre_save.connect(clean_script, sender=Project)
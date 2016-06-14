from contextlib import contextmanager
import six

from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from fabric.api import env, run, execute, cd, local, sudo
from fabric.contrib.files import append
from redis import Redis
from bash import bash
from autoslug import AutoSlugField

from django_extensions.db.models import TimeStampedModel
from django_gravatar.helpers import get_gravatar_url, has_gravatar, get_gravatar_profile_url, calculate_gravatar_hash


from branches import *
from branches.tasks import *
from branches.networking import *
from branches.git import Repo
from branches.celery import get_new_task_id

class OwnerMixin(object):

    def set_owner(self, owner):
        if isinstance(owner, six.string_types):
            owner = get_user_or_team(owner)
        if isinstance(owner, get_user_model()):
            self.user = owner
        elif isinstance(owner, Team):
            self.team = owner

    def get_owner(self):
        return self.team if self.team else self.user

    owner = property(get_owner, set_owner)


class UserProfile(TimeStampedModel):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name="profile")
    gravatar_url = models.URLField(blank=True, null=True)
    rackspace_username = models.CharField(max_length=255, blank=True, null=True)
    rackspace_api_key = models.CharField(max_length=255, blank=True, null=True)
    digitalocean_access_token = models.CharField(
        max_length=255, blank=True, null=True)
    digitalocean_refresh_token = models.CharField(
        max_length=255, blank=True, null=True)
    digitalocean_access_token_expiry = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get_profile(user):
        """ Returns (creates if necessary) a profile for the user
        """
        profile,_ = UserProfile.objects.get_or_create(user=user)
        profile.gravatar_url = get_gravatar_url(user.email)
        profile.save()
        return profile


class Team(TimeStampedModel):

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, related_name="owned_teams")

    @property
    def email(self):
        return self.owner.email

    @property
    def username(self):
        return self.name

    @staticmethod
    def create_team(name, owner):
        """ Creates a team, ensuring no user has that username or other team
        """
        if not name or not owner:
            raise ValueError("Please provide a name and an owner for the team")
        if " " in name:
            raise ValueError("Spaces are not allowed in team names")
        if get_user_model().objects.filter(username=name).exists():
            raise ValueError("That name is already taken")
        if Team.objects.filter(name=name).exists():
            raise ValueError("That name is already taken")
        team = Team.objects.create(name=name, owner=owner)
        team.users.add(owner)
        return team


class Project(OwnerMixin, TimeStampedModel):
    """ A project links several servers toegether. This is analagous to a
        repository stored in say BitBucket or GitHub.
    """
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False)
    change_branch_script = models.ForeignKey(
        "Script", blank=True, null=True, related_name="change_branch_projects")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, editable=False,
        null=True, related_name="projects")
    team = models.ForeignKey(
        Team, blank=True, null=True, editable=False, related_name="projects")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "branches:project-detail", kwargs=dict(owner=self.owner))


class Script(OwnerMixin, TimeStampedModel):
    """ A script that may be executed against a server
    """
    project = models.ForeignKey("Project", related_name="scripts")
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="title")
    text = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, editable=False,
        null=True, related_name="scripts")
    team = models.ForeignKey(
        Team, blank=True, null=True, editable=False, related_name="scripts")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, 
        related_name="authored_scripts")


class Repository(TimeStampedModel):
    """ This object represents a repository on the user / team's account
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    branch = models.CharField(
        max_length=255, blank=True, null=True, editable=False)
    previous_branch = models.CharField(
        max_length=255, blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.name

class Server(OwnerMixin, TimeStampedModel):
    """ Servers have GIT projects on them that users want to change branches
        for. 
    """
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', editable=False)
    project = models.ForeignKey(
        "Project", related_name="servers")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, editable=False,
        related_name="servers")
    team = models.ForeignKey(
        Team, blank=True, null=True, editable=False, related_name="servers")
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    port = models.PositiveIntegerField(default=22)
    repository = models.OneToOneField(
        Repository, blank=True, null=True, 
        related_name="server", editable=False)
    initialized = models.BooleanField(default=False, editable=False)

    def __unicode__(self):
        return self.name

    def connect(self):
        """ A context manager that allows connection to the server
        """
        return setup_fabric_environment(
            self.address, 
            username=self.username,
            port=self.port)

    @property
    def location(self):
        return self.repository.location

    @property
    def change_branch_script(self):
        return self.project.change_branch_script

    def execute(self, cmd):
        """ Runs a command on the server via the Celery process.
        """
        pass

    def initialize(self, username, password, port=None):
        """ Copy up the server's key to this server
        """
        result = copy_key_to_server.delay(
            self.pk,
            username=username, password=password, port=port or self.port)
        return result

    def get_absolute_url(self):
        project = self.project
        owner = self.owner.username
        return reverse(
            "branches:server-detail", 
            kwargs=dict(
                owner=owner,
                project=project.slug,
                server=self.slug))

    def get_log(self, limit=7):
        """ Returns `limit` lines of the last log of a script that was running
        """
        log = self.logs.filter(execution__active=True).last()
        return log.get_log(limit=limit) if log else ""


    @property
    def is_script_running(self):
        """ Tells us if we are changing the branches for this project
        """
        return self.executions.filter(active=True).exists()

    @property
    def requests_exists(self):
        """ Returns true if a branch change has been requested
        """
        return self.requests.\
            filter(status=Request.STATUS_REQUESTED).exists()

    @property
    def log(self):
        """ The log of the change branch script
        """
        return self.logs.filter(execution__active=True).last()


    def cancel_execution(self):
        """ Cancel the currently running execution
        """
        for execution in self.executions.filter(active=True):
            execution.cancel()
            return True
        return False

    @property
    def repo(self):
        """ Return a repository object, only for use when connected to a server
        """
        return Repo(self.repository.location)

    @property
    def current_branch(self):
        """ Returns the branch the server is currently on
        """
        with self.connect():
            def get_current_branch():
                with cd(self.location):
                    return self.repo.active_branch
            result = execute(get_current_branch)
            return result.get(self.address)
        return None

    @property
    def available_branches(self):
        """ Returns a dictionary with available_branches and current_branch
        """
        with self.connect():
            def get_available_branches():
                with cd(self.location):
                    return self.repo.available_branches
            result = execute(get_available_branches)
            return result.get(self.address)
        return None

    def get_status(self, limit=10):
        """ Return about whether we're changing branches, whether a branch
            change has been requested and some other details.
        """
        with self.connect():
            def get_status():
                with cd(self.location):
                    return self.repo.get_status(limit=limit)
            result = execute(get_status)
            result = result.get(self.address)
            result["log"] = self.get_log(limit=limit)
            result["is_script_running"] = self.is_script_running
            result["requests_exists"] = self.requests_exists
            return result
        return None

    def request_branch_change(self, branch):
        """ Request a branch change
        """
        if self.requests_exists:
            raise Exception("Another request exists")
        task_id = get_new_task_id() # generate a uuid
        request = Request.objects.create(
            project=self,
            branch=branch,
            task_id=task_id)
        task_args = [self.pk, branch, request.pk]
        result = change_server_branch.apply_async(args=task_args,
            task_id=task_id)
        return request

    def change_branch(self, branch, task_id, request_pk):
        """ This method is executed by the ``change_server_branch`` task in
            the Celery process. 
        """
        executions = self.executions.filter(active=True)
        # Make sure there are no other executions running
        for execution in executions:
            other_task_id = execution.task_id
            # check if this tsak is complete first
            result = change_server_branch.AsyncResult(other_task_id)
            if not result.ready():
                print("Another execution %s is still running, "
                      "cannot change branch" % other_task_id)
                return False
            # Set this as inactive then
            execution.active = False
            execution.save()
        # Double check that none are active, in case another worker started
        if self.executions.filter(active=True).exists():
            print("Someone beat us to it.. can't change branch")
            return False

        try:
            request = Request.objects.get(pk=request_pk)
            if not request.requested:
                """ At this point we expect the request to be requested, if it's 
                    not it means that either:
                    - Some other worker has actioned the request
                    - It has been cancelled
                """
                print("Not actioning this request, it currently has status: %s" % \
                        request.status)
                return False
            print("Request status is: %s" % request.status)
        except Request.DoesNotExist:
            print("If this request does not exist, don't continue")
            return False
        current_branch = self.branch
        # Create a chnge log and mark it as active
        log = Log.objects.create(server=self,
            branch=current_branch)
        request.log = log
        request.status = Request.STATUS_IN_PROGRESS
        request.save()

        print("Asked to change branch from %s to %s" % (current_branch, branch))
        # Make sure the media root directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        script_filename = "%s/server_log_%s_%s.log" % \
            (settings.MEDIA_ROOT, self.pk, log.pk)
        user_script_filename = "script_%s.sh" % log.pk
        log.log_filename = script_filename
        log.save()
        with self.connect():
            with cd(self.location):
                # Create the log file
                with open(script_filename, "w") as log_file:
                    if self.project.change_branch_script:
                        execution = Execution.objects.create(
                            server=self, 
                            log=log,
                            request=request)
                    else:
                        execution = None

                    def change_branch_task():
                        log_file.write("Changing branch from %s to %s\r\n" % \
                                (current_branch, branch))
                        log_file.write("Discarding local changes...\r\n")
                        run("git checkout -- .", stdout=log_file)
                        log_file.write("Changing branch to %s\r\n" % branch)
                        run("git checkout %s" % branch, stdout=log_file)
                        self.branch = branch
                        self.save()
                        # check if the branch exists on origin
                        run("git pull", stdout=log_file, warn_only=True)
                        if self.project.change_branch_script:
                            log_file.write("Running custom script\r\n")
                            run("rm %s" % user_script_filename, warn_only=True)
                            run("touch %s" % user_script_filename)
                            append(
                                user_script_filename, 
                                self.project.change_branch_script.text)
                            run("chmod +x %s" % user_script_filename)
                            sudo("./%s" % user_script_filename, stdout=log_file)
                    try:
                        execute(change_branch_task)
                    except Exception as e:
                        print("Exception occurred changing branches: %s" % e)
                        log_file.write(e.message)
                        return False
                    finally:
                        request.status = Request.STATUS_COMPLETE
                        request.save()
                        execution.active = False
                        execution.save()
        return True

    def get_commits(self, limit=10):
        """ Gets the commits for the current branch
        """
        with self.connect():
            with cd(self.location):
                def _get_commits():
                    return self.repo.get_commits(limit=limit)
                result = execute(_get_commits)
                return result.get(self.address)
        return []

    @property
    def last_request(self):
        """ Returns the last request to change a branch if any exists
        """
        try:
            return self.requests.latest("created")
        except Request.DoesNotExist:
            return None

    def update_branch_list(self):
        with self.connect():
            def fetch():
                with cd(self.location):
                    self.repo.fetch()
                    return self.repo.available_branches
            result = execute(fetch)
            return result.get(self.address)
        return None


class Log(TimeStampedModel):

    server = models.ForeignKey("Server", related_name="logs")
    branch = models.CharField(max_length=255)
    log_filename = models.FileField(blank=True, null=True)

    def get_log(self, limit=50):
        """ Gets the last limit lines of the log file
        """
        result = unicode(bash("tail -n %s %s" % (limit, self.log_filename.url)))
        result = result.replace("\n", "<br>")
        result = result.replace("\r", "")
        return result


class Request(TimeStampedModel):
    """ A request to run a script
    """

    STATUS_REQUESTED = "requested"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_COMPLETE = "complete"
    STATUS_CANCELLED = "cancelled"

    server = models.ForeignKey("Server", related_name="requests")
    branch = models.CharField(max_length=255)
    status = models.CharField("Status", max_length=50, default=STATUS_REQUESTED)
    log = models.OneToOneField("Log", 
        blank=True, null=True)
    #: The ID of the celery task executing the request
    task_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, editable=False,
        null=True, related_name="requests")


    def cancel(self):
        # Terminate the task 
        result = change_server_branch.AsyncResult(self.task_id)
        if not result.ready():
            print("Terminating the task")
            result.revoke(terminate=True)
        print("Marking ourselves as cancelled")
        self.status = Request.STATUS_CANCELLED
        self.save()
        return True

    @property
    def complete(self):
        return self.status == Request.STATUS_COMPLETE

    @property
    def requested(self):
        return self.status == Request.STATUS_REQUESTED

    @property
    def cancelled(self): 
        return self.status == Request.STATUS_CANCELLED

    @property
    def in_progress(self):
        return self.status == Request.STATUS_IN_PROGRESS


class Execution(TimeStampedModel):
    """ This model records the execution of a ``Script`` against a server.
    """
    script = models.ForeignKey(Script, related_name="executions")
    server = models.ForeignKey(Server, related_name="executions")
    request = models.OneToOneField(
        Request, related_name="execution", blank=True, null=True)
    log = models.OneToOneField("Log", 
        blank=True, null=True)
    active = models.BooleanField(default=True)

    def cancel(self):
        """ Cancels the execution of the script
        """
        return self.request.cancel()


def clean_script(sender, instance, **kwargs):
    """ Remove any weird spaces from the script
    """
    print("Cleaning script")
    raw = kwargs.get("raw")
    if raw:
        return
    script = instance.text
    if not script:
        return
    clean_line = lambda line: line.strip() + "\n"
    script = "".join(map(clean_line, script.splitlines()))
    instance.text = script
pre_save.connect(clean_script, sender=Script)


def get_user_or_team(username):
    """ Returns a user or team given the username
    """
    try:
        team = Team.objects.get(name=username)
        return team
    except Team.DoesNotExist:
        user = get_user_model().objects.get(username=username)
        return user
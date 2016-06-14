from fabric.api import env, run, execute, cd
from fabric.contrib.files import append

from .networking import setup_fabric_environment, test_credentials
from .system import get_ssh_key
from branches.celery import app


@app.task()
def copy_key_to_server(server_pk, username, password, port):
    """ Copies our key to the server
    """
    from branches.models import Server
    server = Server.objects.get(pk=server_pk)
    print("Connecting to %s with %s on port: %s" %
          (server.address, username, port))
    if not test_credentials(server.address, username, password, port):
        print("Credentials failed")
        return False
    with server.connect():
        print("Copying up the key now...")
        key = get_ssh_key()
        execute(lambda: append("~/.ssh/authorized_keys", key))
        server.initialized = True
        # Update the port incase it changed
        server.port = port
        server.save()
        return True


@app.task(bind=True)
def change_server_branch(self, server_pk, branch, request):
    from branches.models import Project
    project = Project.objects.get(pk=server_pk)
    return project.change_branch(
        branch, self.request.id, request)



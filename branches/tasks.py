from fabric.api import env, run, execute, cd
from fabric.contrib.files import append

from .networking import connect, test_credentials
from .system import get_ssh_key

def copy_key_to_server(server_pk, username, password, port):
    from branches.models import Server
    server = Server.objects.get(pk=server_pk)
    if not test_credentials(server.address, username, password, port):
        return False

    with connect(server, username, password, port):
        print("Copying up the key now...")
        key = get_ssh_key()
        append_key = lambda : append("~/.ssh/authorized_keys", key)
        execute(append_key)
        server.initialized = True
        server.save()
        return True

def change_server_branch(project_pk, branch):
    from branches.models import Project
    project = Project.objects.get(pk=project_pk)
    return project.change_branch(branch)

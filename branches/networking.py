from fabric.api import env, run, execute, cd
from fabric.contrib.files import append

import paramiko
from paramiko.client import SSHClient

def test_credentials(hostname, username, password, port=22, timeout=15):
	""" Returns True if the credentials work
	"""
	client = SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		client.connect(hostname, username=username, password=password,
			port=port, timeout=10)
		return True
	except Exception as e:
		print(e)
		return False

def test_keyfile(hostname, username, key_filename, port=22, timeout=15):
    """ Tests if a key file works
    """
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, port=port, username=username,
            key_filename=key_filename, timeout=10)
        return True
    except Exception as e:
        print(e)
        return False

class connect(object):
    """ Context manager to allow us to connect to servers
    """

    def __init__(self, server, username=None, password=None, port=22):
        print("Connecting to %s" % server)
        self.server = server
        self.username = username
        self.password = password
        self.port = port

    def __enter__(self):
        # connect to the Server
        env["hosts"] = [self.server.address]
        if self.username and self.password:
            env["user"] = self.username
            env["password"] = self.password
        else:
            env["key_filename"] = get_key_filename()
        env["port"] = self.port

    def __exit__(self, *args, **kwargs):
        pass

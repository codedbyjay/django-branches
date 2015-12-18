import paramiko
from paramiko.client import SSHClient

def test_credentials(hostname, username, password, port):
	""" Returns True if the credentials work
	"""
	client = SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		client.connect(hostname, username=username, password=password,
			port=port)
		return True
	except Exception as e:
		print(e)
		return False

class connect(object):

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
            env["key_filename"] = get_pem_filename()
        env["port"] = self.port

    def __exit__(self, *args, **kwargs):
        pass

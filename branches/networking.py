from fabric.api import env, run, execute, cd
from fabric.contrib.files import append

import paramiko
from paramiko.client import SSHClient

from .system import *


def test_credentials(hostname, username, password, port=22, timeout=15):
    """ Returns True if the credentials work
    """
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname, username=username, password=password,
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
        client.connect(
            hostname, port=port, username=username,
            key_filename=key_filename, timeout=10)
        return True
    except Exception as e:
        print(e)
        return False


def setup_fabric_environment(address, username=None, password=None, port=22):
    env["hosts"] = [address]
    env["user"] = username
    if username and password:
        env["password"] = password
    else:
        env["key_filename"] = get_key_filename()
    env["port"] = port


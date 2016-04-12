import os

from django.conf import settings

from bash import bash


def get_ssh_key():
    key_location = settings.SSH_KEY_LOCATION
    key_file = "%s/id_rsa.pub" % key_location
    if os.path.exists(key_file):
        key = open(key_file).read()
        return key
    return None


def generate_ssh_key():
    key_location = settings.SSH_KEY_LOCATION
    bash("ssh-keygen -t rsa -N '' -q -f %s/id_rsa" % key_location)
    bash(
        "ssh-keygen -f %s/id_rsa -e -m pem > %s/id_rsa.pub.pem"
        % (key_location, key_location))

key = get_ssh_key()
if not key:
    print("Generating a SSH key for you")
    generate_ssh_key()


def get_key_filename():
    key_location = settings.SSH_KEY_LOCATION
    key_file = "%s/id_rsa" % key_location
    return key_file

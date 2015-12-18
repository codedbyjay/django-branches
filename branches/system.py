import os

from bash import bash

def get_ssh_key():
	key_location = os.path.expanduser("~/.ssh/id_rsa.pub")
	if os.path.exists(key_location):
		key = open(key_location).read()
		return key
	return None

def generate_ssh_key():
	bash("ssh-keygen -t rsa -N '' -q -f ~/.ssh/id_rsa")
	bash("ssh-keygen -f ~/.ssh/id_rsa -e -m pem > ~/.ssh/id_rsa.pub.pem")

key = get_ssh_key()
if not key:
	print("Generating a SSH key for you")
	generate_ssh_key()

def get_key_filename():
	return os.path.expanduser("~/.ssh/id_rsa")

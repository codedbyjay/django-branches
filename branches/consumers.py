import json

from django.http import HttpResponse
from django.contrib import auth

from channels import Group
from channels.auth import (
    channel_session_user_from_http, channel_session_user,
    http_session_user
)
from channels.sessions import channel_session, session_for_reply_channel
from channels.generic.websockets import JsonWebsocketConsumer

from branches.tasks import get_server_status
from branches.models import Server


class ServerDetailPageConsumer(JsonWebsocketConsumer):
    """ This consumer servers up details for the server detail page
    """

    channel_session_user = True

    def get_handler(self, message, **kwargs):
        """
        Return handler uses method_mapping to return the right method to call.
        """
        handler = getattr(self, self.method_mapping[message.channel.name])
        if self.channel_session_user:
            if message.channel.name == 'websocket.connect':
                return channel_session_user_from_http(handler)
            return channel_session_user(handler)
        elif self.channel_session:
            return channel_session(handler)
        else:
            return handler

    def connection_groups(self, **kwargs):
        """ Returns a list of groups all sockets visiting this page must be
            added to.
        """
        server = kwargs.get("server")
        print("Adding to channel for server with pk=%s" % (server))
        return ["server-%s" % server]

    def connect(self, message, **kwargs):
        slug = kwargs.get("server")
        self.server = Server.objects.get(slug=slug)

    def receive(self, content, **kwargs):
        print("Received content: %s from %s" % (content, self.message.user))
        message_type = content.get("type")
        print("Got message of type: %s" % message_type)
        handler = getattr(self, message_type.replace("-", "_"))
        handler(content, **kwargs)

    def request_server_status(self, content, **kwargs):
        Group("server-%s" % server.pk).send(server.get_status())


@channel_session_user_from_http
def ws_connect(message):
    print("ws_connect: User connected: %s" % message.user)
    user = message.user
    print(message.channel_session)
    # Group("online").add(message.reply_channel)
    # Group("chat").add(message.reply_channel)


@channel_session_user_from_http
def server_page(message, server=None):
    print("User %s connected to server page for %s" % (message.user, server))


@channel_session_user
def server_page_disconnect(message, server=None):
    print("User %s disconnected to server page for %s" %
          (message.user, server))


@channel_session_user
def ws_receive(message):
    user = message.user
    text = message.content['text']
    username = message.user.username
    print("%s sent message: %s" % (message.user, text))
    try:
        obj = json.loads(text)
        message_type = obj.get("type")
        server = obj.get("server")
        server_group = Group("server-%s" % server).add(message.reply_channel)
        get_server_status.delay(server)
    except ValueError:
        pass


@channel_session_user
def ws_disconnect(message):
    user = message.user
    print("%s went offline" % user)

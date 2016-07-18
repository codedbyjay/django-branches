from channels import route, route_class

from branches.consumers import ServerDetailPageConsumer

channel_routing = [
    # route_class(ServerDetailPageConsumer, path="^/server/(?P<server>[\w\-_]+)"),
    route_class(ServerDetailPageConsumer, path="^/(?P<owner>[\w\-_])+/(?P<project>[\w\-_]+)/(?P<server>[\w\-_]+)"),
    # route("websocket.connect", "branches.consumers.server_page", path="^/server/(?P<server>[\w\-_]+)"),
    route("websocket.disconnect", "branches.consumers.server_page_disconnect", path="^/server/(?P<server>[\w\-_]+)"),
    route("websocket.receive", "branches.consumers.ws_receive"),
]
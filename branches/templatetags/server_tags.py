from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def server_log(server):
    ctx = {
        "server" : server
    }
    return render_to_string("branches/server_log.html", ctx)


@register.simple_tag
def render_server(server, full=False, show_actions=False):
    """ Renders the server using the server_panel template, 
        passing all the variables pass to us here.
    """
    ctx = {
        "server" : server,
        "show_actions" : show_actions,
    }
    return render_to_string("branches/server_panel.html", ctx)

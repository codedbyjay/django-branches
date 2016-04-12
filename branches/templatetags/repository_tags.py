from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def render_repository(repository, full=False):
    ctx = {
        "repository" : repository
    }
    return render_to_string("branches/repository_panel.html", ctx)

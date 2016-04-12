from django import template
from django.template.loader import render_to_string

from branches.forms import ChangeBranchForm

register = template.Library()

@register.simple_tag
def render_project(project, full=False, show_commits=False):
    ctx = {
        "project" : project,
        "show_commits" : show_commits,
        "full" : full,
        "change_branch_form" : ChangeBranchForm()
    }
    return render_to_string("branches/project_panel.html", ctx)

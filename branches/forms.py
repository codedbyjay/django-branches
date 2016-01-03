from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, HTML, Div
from crispy_forms.bootstrap import FormActions

from fabric.api import env, run, execute, cd

from branches.models import *

class NewServerForm(ModelForm):

    class Meta:
        model = Server
        fields = ["name", "address", "description", "port"]
        exclude = ["initialized"]

    def __init__(self, *args, **kwargs):
        result = super(NewServerForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<span class='title'>Create a server</span>"),
                    HTML("<span class='instructions'>Enter the details about your server</span>"),
                    css_class='form-header'),
                'name',
                'address',
                'description',
                'port',
                FormActions(
                    Button('cancel', 'Cancel', onclick="javascript:window.history.back()"),
                    Submit('save', 'Save'),
                    css_class="form-actions"
                ),
            css_class='branches-form'),
        )
        return result


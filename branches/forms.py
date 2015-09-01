from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button
from crispy_forms.bootstrap import FormActions

from fabric.api import env, run, execute, cd

from branches.models import *

class NewServerForm(ModelForm):

    class Meta:
        model = Server
        fields = ["name", "address", "description", "port"]
        exclude = ["intialized"]

    def __init__(self, *args, **kwargs):
        result = super(NewServerForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)
        if not instance:
            # This means it's a new server
            self.fields["username"] = forms.CharField()
            self.fields["password"] = forms.CharField(widget=forms.PasswordInput)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'address',
            'description',
            'username', 
            'password',
            'port',
            FormActions(
                Submit('save', 'Save'),
                Button('cnacel', 'Cancel')
            )
        )
        return result


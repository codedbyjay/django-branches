from django import forms
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, HTML, Div, Field
from crispy_forms.bootstrap import FormActions

from fabric.api import env, run, execute, cd

from registration.forms import RegistrationForm as CoreRegistrationForm

from branches.models import *


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            FormActions(
                Submit('login', 'Login'),
            ),
        )


class RegistrationForm(CoreRegistrationForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'password1',
            'password2',
            FormActions(
                Submit('signup', 'Create Account'),
            ),
        )


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

class InitializeServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = ["address", "username", "port"]
    address = forms.CharField(label="Server Address")
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    port = forms.IntegerField()

    def __init__(self, server, *args, **kwargs):
        self.server = server
        result = super(InitializeServerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<span class='title'>Initialize server</span>"),
                    HTML("<span class='instructions'>Now we need to initialize your server</span>"),
                    css_class='form-header'),
                'address',
                'username',
                'password',
                'port',
                Div(css_class='server-log'),
                FormActions(
                    Submit('login', 'Login'),
                ),
            css_class='branches-form'),
        )
        return result

    def clean(self):
        # check if the username and password work
        cleaned_data = self.cleaned_data
        address = cleaned_data.get("address")
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        port = cleaned_data.get("port")
        if not test_credentials(address, username, password, port=port):
            raise forms.ValidationError("Ooops.. we didn't get into the server with those credentials")
        return cleaned_data

class NewProjectForm(ModelForm):

    class Meta:
        model = Project
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.username = self.user.username
        result = super(NewProjectForm, self).__init__(*args, **kwargs)
        choices = [(self.username, self.username)]
        for team in self.user.teams.all():
            choices.append((team.name, team.name))
        select = forms.Select(choices=choices)
        self.fields["owner"] = forms.CharField(widget=select)
        self.fields["change_branch_script"] = forms.CharField(
            widget=forms.Textarea, required=False)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<span class='title'>New Project</span>"),
                    HTML("<span class='instructions'>Enter the details for your project</span>"),
                    css_class='form-header'),
                'owner',
                'name',
                'change_branch_script',
                FormActions(
                    Submit('create', 'Add Project'),
                ),
            css_class='branches-form'),
        )
        return result

    def save(self, commit=True):
        owner = self.cleaned_data.pop("owner")
        change_branch_script = self.cleaned_data.pop("change_branch_script")
        instance = super(NewProjectForm, self).save(commit=False)
        instance.owner = owner
        instance.save()
        if instance.change_branch_script:
            script = instance.change_branch_script
            script.text = change_branch_script
            script.save()
        else:
            script_kwargs = {
                "project": instance,
                "title": "%s change branch script" % instance,
                "text": change_branch_script,
                "author": self.user,
            }
            script = Script(**script_kwargs)
            script.owner = owner
            script.save()
            instance.change_branch_script = script
            instance.save()




class ChangeBranchForm(forms.Form):

    branch = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        result = super(ChangeBranchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'branch',
        )
        return result
    


class NewRepositoryForm(ModelForm):

    class Meta:
        model = Repository
        fields = ["name", "url"]

    def __init__(self, *args, **kwargs):
        result = super(NewRepositoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<span class='title'>New Repository</span>"),
                    HTML("<span class='instructions'>Enter the details for your repository</span>"),
                    css_class='form-header'),
                'name',
                'url',
                FormActions(
                    Submit('create', 'Add Repository'),
                ),
            css_class='branches-form'),
        )
        return result


class RackspaceConnectForm(forms.Form):

    username = forms.CharField(initial="monainformatix")
    api_key = forms.CharField(initial="0fc3f1cf815af6c75d7e3f75067d283f")

    def __init__(self, *args, **kwargs):
        result = super(RackspaceConnectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("<span class='title'>Rackspace Connect</span>"),
                    HTML("<span class='instructions'>Enter your username and API key</span>"),
                    css_class='form-header'),
                'username',
                'api_key',
                FormActions(
                    Submit('create', 'Connect to Rackspace'),
                ),
            css_class='branches-form'),
        )
        return result

    def clean(self):
        """ Verify that the credentials works
        """
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        api_key = cleaned_data.get("api_key")
        pyrax.set_setting("identity_type", "rackspace")
        try:
            print("Testing Rackspace credentials for: %s" % username)
            pyrax.set_credentials(username, api_key)
        except pyrax.exc.AuthenticationFailed:
            raise forms.ValidationError(
                "Incorrect API key or userame")
        return cleaned_data




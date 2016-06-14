from django.views.generic import TemplateView, FormView
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from registration.backends.hmac.views import (
    RegistrationView as CoreRegistrationView
)

from branches.forms import LoginForm, RegistrationForm
from branches.views import ProjectListView


class HomeView(ProjectListView):

    template_name = "branches/project_list.html"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            self.template_name = "branches/home.html"
        return super(HomeView, self).get(request, *args, **kwargs)


class RegistrationView(CoreRegistrationView):

    form_class = RegistrationForm

class LogoutView(TemplateView):

    template_name = "branches/logout.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            logout(self.request)
        return super(LogoutView, self).get(*args, **kwargs)


class LoginView(FormView):

    form_class = LoginForm
    template_name = "branches/login.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect("dashboard", username=self.request.user.username)
        return super(LoginView, self).get(*args, **kwargs)

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("dashboard", username=self.request.user.username)
        else:
            print("Invalid user")
            form.add_error(None, "Invalid email or password")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


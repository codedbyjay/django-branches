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

    template_name = "branches/home.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.template_name = "branches/dashboard.html"
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ctx["page"] = "home"
        return ctx


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
            return redirect("home")
        return super(LoginView, self).get(*args, **kwargs)

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("home")
        else:
            form.add_error(None, "Invalid email or password")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


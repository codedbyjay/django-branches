from django.views.generic import TemplateView, FormView
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from registration.backends.hmac.views import (
    RegistrationView as CoreRegistrationView
)

from branches.forms import LoginForm, RegistrationForm


def home(request):
    return render_to_response("branches/home.html")


class DashboardView(TemplateView):

    template_name = "branches/dashboard.html"


class RegistrationView(CoreRegistrationView):

    form_class = RegistrationForm


class LoginView(FormView):

    form_class = LoginForm
    template_name = "branches/login.html"

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("dashboard")
        else:
            print("Invalid user")
            form.add_error(None, "Invalid email or password")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


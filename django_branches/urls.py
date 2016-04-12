from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static

from django_branches.views import LoginView, DashboardView, RegistrationView


urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', 'django_branches.views.home', name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^accounts/register/$', RegistrationView.as_view(), name='register'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Both urls needed for branches to work
    url(r'^branches/', include('branches.urls', namespace="branches")),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
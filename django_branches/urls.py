from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'django_branches.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),

    # Both urls needed for branches to work
    url(r'^branches/', include('branches.urls', namespace="branches")),

) +  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


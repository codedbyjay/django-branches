from django.contrib import admin

from branches.models import *

admin.site.register(Server)
admin.site.register(Repository)
admin.site.register(Project)

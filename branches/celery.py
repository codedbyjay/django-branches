from __future__ import absolute_import
import os

from django.conf import settings
from celery import Celery
from celery import uuid
from celery.signals import celeryd_after_setup
from celery.schedules import crontab
from kombu import Exchange, Queue


def get_new_task_id():
    return uuid()


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_branches.settings')

app = Celery('branches')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_TIMEZONE=settings.TIME_ZONE,
    BROKER_URL=settings.BROKER_URL,
    CELERY_TASK_RESULT_EXPIRES=18000,
    CELERY_RESULT_BACKEND='redis://redis'
)

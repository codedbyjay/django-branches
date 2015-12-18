from __future__ import absolute_import
import os

from django.conf import settings
from celery import Celery
from celery.signals import celeryd_after_setup
from celery.schedules import crontab
from kombu import Exchange, Queue
from autodiscovery_module import autodiscover

# Define some constants
BROKER_USER = "branches"
BROKER_PASSWORD = "branches"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_URL = "amqp://%s:%s@%s:%s//" % \
	(BROKER_USER, BROKER_PASSWORD, BROKER_HOST, BROKER_PORT)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_branches.settings')

app = Celery('excess')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
	CELERY_TIMEZONE=settings.TIME_ZONE,
	BROKER_URL=BROKER_URL,
	CELERY_BACKEND="amqp",
	CELERY_TASK_RESULT_EXPIRES=18000, # 5 hours
)

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from testproject import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{settings.PROJECT_NAME}.settings')

app = Celery(settings.PROJECT_NAME)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

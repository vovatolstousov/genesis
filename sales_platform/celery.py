from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from celery.schedules import crontab
from .settings import BROKER_URL

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_platform.settings')
# from django.conf import settings
# settings.configure()

import django
django.setup()

app = Celery(
    'sales_platform',
    broker=BROKER_URL,
    backend='amqp://',
    include=['sales_platform.tasks']
)

app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'delete-expired-orders': {
        'task': 'sales_platform.tasks.overdue_orders',
        'schedule': crontab(minute='*/15'),
    },
    'user-activity-check': {
        'task': 'sales_platform.tasks.user_online_status_trigger',
        'schedule': crontab(minute='*/10'),
    },
    # 'delete_expired_unverificated_user': {
    #     'task': 'sales_platform.tasks.delete_expired_unverificated_user',
    #     'schedule': 30.0,
    # }
}
# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'sales_platform.tasks.add',
#         'schedule': 30.0,
#         'args': (16, 16)
#     },
# }

app.conf.timezone = 'UTC'

if __name__ == '__main__':
    app.start()

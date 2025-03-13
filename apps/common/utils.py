import shutil
from django.core.cache import cache
from django.db import connections
from rest_framework.reverse import reverse as drf_reverse
from typing import Callable

from testproject import celery


def run_once():
    has_run = False

    def inner(func) -> Callable:
        def wrapped(*args, **kwargs):
            nonlocal has_run
            if not has_run:
                has_run = True
                return func(*args, **kwargs)

        return wrapped

    return inner


class HealthCheck:
    def disk(self, stats=False):
        """Check the percentage of filesystem storage remaining."""
        total, used, free = shutil.disk_usage('/')
        used_percentage = (used / total) * 100
        free_percentage = (free / total) * 100
        if stats:
            return {
                'total_space': total,
                'used_space': used,
                'free_space': free,
                'used_percentage': used_percentage,
                'free_percentage': free_percentage
            }
        return free_percentage < 90

    def database(self):
        # Postgres
        postgres = 0
        try:
            db_conn = connections['default']
            db_conn.cursor()
            postgres = 1
        except Exception as e:
            # sentry_sdk.capture_event({"postgres": "Postgres Server not available"})
            print(">>>", "Postgres not available")

        if postgres:
            return 1
        else:
            return 0

    def cache(self):
        odd_key = '-----|-----123'
        ok = 'OK'
        try:
            cache.set(odd_key, ok)
            is_ok = cache.get(odd_key)
            return is_ok == ok
        except Exception as e:
            # TODO: sentry
            return False

    def celery(self) -> bool:
        """Check if Celery workers are alive."""
        try:
            response = celery.app.control.ping(timeout=2)
            return bool(response)  # True if workers responded, False otherwise
        except Exception as e:
            # TODO: sentry
            print(str(e))
            return False

    @classmethod
    def all(cls):
        health = cls()
        return dict(
            cache=health.cache(),
            db=health.database(),
            disk=health.disk(),
            celery=health.celery(),
        )


def reverse(url_name, version='v1', **kwargs):
    return drf_reverse(url_name, kwargs={'version': version, **kwargs}, )

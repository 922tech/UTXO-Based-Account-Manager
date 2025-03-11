from django.core.management.base import BaseCommand
from apps.common.utils import HealthCheck


class Command(BaseCommand):
    help = 'Checking the health of dependant services.'

    def handle(self, *args, **kwargs):

        status = HealthCheck.all()
        for k, h in status.items():
            if h:
                self.stdout.write(self.style.SUCCESS(f'- {k} is healthy'))
            else:
                self.stdout.write(self.style.ERROR(f'- {k} is unhealthy'))

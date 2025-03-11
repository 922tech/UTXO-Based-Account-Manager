from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Describe what your command does here.'

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(username='default_storage')
        token, _ = Token.objects.get_or_create(user=user)
        Token.objects.filter(user=user).update(key=settings.CLOUD_STORAGE_CLIENT_CONFIG['default_storage_token'])
        self.stdout.write(self.style.SUCCESS('Storage configured successfully successfully!'))


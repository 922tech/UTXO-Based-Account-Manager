from django.db.models.signals import post_migrate, class_prepared
from django.dispatch import receiver

from .models import Config


@receiver(post_migrate)
def create_ai_models(sender, **kwargs):
    config = Config.get_instance().config
    if not 'storage_id' in config:
        pass

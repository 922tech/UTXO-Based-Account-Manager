from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.users.models import Account


@receiver(pre_save, sender=Account)
def encrypt_private_key(sender, instance, **kwargs):
    if instance.private_key:
        instance.encrypt_private_key()


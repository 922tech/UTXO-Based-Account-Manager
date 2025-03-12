from django.conf import settings
from django.db.models.signals import pre_save, post_migrate
from django.dispatch import receiver

from apps.common.utils import run_once
from apps.users.models import Account, User


@receiver(pre_save, sender=Account)
def encrypt_private_key(sender, instance, **kwargs):
    if instance.private_key:
        instance.encrypt_private_key()


@receiver(post_migrate)
@run_once()
def create_admin_account(sender, **kwargs):
    """
    Creates the admin account if it does not exist (seeds the database)
    """
    if not Account.objects.filter(uuid=settings.ADMIN_ACCOUNT_UUID).first():
        admin_username = 'crypto_admin'
        crypto_admin = User.objects.filter(username=admin_username).first()
        if not crypto_admin:
            crypto_admin = User.objects.create_user(username=admin_username)
        Account.objects.create(user=crypto_admin, uuid=settings.ADMIN_ACCOUNT_UUID)
        print("admin account created")

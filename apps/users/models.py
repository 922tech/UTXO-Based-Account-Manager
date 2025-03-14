import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from apps.common.cache import Cache
from apps.common.crypto import Encryptor, DigitalSigner
from apps.common.models import BaseModel

User = get_user_model()


class AccountManager(models.Manager):
    def admin_account(self):
        cache = Cache()
        admin_uuid = settings.ADMIN_ACCOUNT_UUID
        admin_account = cache.get_for_id(Cache.Account, admin_uuid, default=0)
        if not admin_account:
            admin_account = self.get(uuid=admin_uuid)
            cache.set_for_id(Cache.Account, admin_uuid, value=admin_uuid)

        return admin_account


class Account(BaseModel):
    objects = AccountManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    private_key = models.TextField()
    public_key = models.TextField()
    bank_account = models.CharField(max_length=255)

    def _handle_defaults(self):
        if self.created_at is None:
            key_pair = DigitalSigner.generate_key_pair()
            self.private_key = key_pair['private']
            self.public_key = key_pair['public']

    def save(self, *args, **kwargs):
        self._handle_defaults()
        # NOTE: encryption is handled by a signal so don't worry about it
        return super().save(*args, **kwargs)

    def encrypt_private_key(self):
        encryptor = Encryptor()
        self.private_key = encryptor.encrypt(self.private_key)

    def decrypt_private_key(self):
        encryptor = Encryptor()
        self.private_key = encryptor.decrypt(self.private_key)
        return self.private_key

    class Meta:
        ordering = ('-id',)

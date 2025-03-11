from django.contrib.auth import get_user_model
from django.db import models

from apps.common.crypto import Encryptor, DigitalSigner
from apps.common.models import BaseModel

User = get_user_model()


class Account(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    private_key = models.TextField()
    public_key = models.TextField()

    def _handle_defaults(self):
        if self.created_at is None:
            key_pair = DigitalSigner.generate_key_pair()
            self.private_key = key_pair['private']
            self.public_key = key_pair['public']

    def save(self, *args, **kwargs):
        self._handle_defaults()
        return super().save(*args, **kwargs)

    def encrypt_private_key(self):
        encryptor = Encryptor()
        self.private_key = encryptor.encrypt(self.private_key)

    def decrypt_private_key(self):
        encryptor = Encryptor()
        self.private_key = encryptor.decrypt(self.private_key)

    class Meta:
        ordering = ('-id',)

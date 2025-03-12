from django.db import models
from django.db.models import IntegerChoices

from apps.common.models import BaseModel


class TxStatusChoices(IntegerChoices):
    PENDING = 0, 'Pending'
    COMPLETED = 1, 'Completed'
    FAILED = 2, 'Failed'


class TxVersionChoices(IntegerChoices):
    V1 = 1, '1'


class Transaction(BaseModel):
    version = models.IntegerField(choices=TxVersionChoices.choices, default=TxVersionChoices.V1)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=TxStatusChoices.choices, default=TxStatusChoices.PENDING)


class TxInput(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='inputs')
    prev_tx = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    vout = models.PositiveIntegerField()  # Output index from previous transaction
    script_sig = models.TextField(blank=True, null=True)


class TxOutput(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='outputs')
    value = models.BigIntegerField()  # Value in satoshis
    script_pub_key = models.TextField(help_text='the target wallet public key')

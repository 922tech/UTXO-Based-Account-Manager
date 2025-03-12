from django.contrib.postgres.indexes import HashIndex
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
    status = models.IntegerField(choices=TxStatusChoices.choices, default=TxStatusChoices.PENDING)


class TxInput(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='inputs')
    prev_tx = models.ForeignKey(Transaction, on_delete=models.PROTECT, null=True, related_name='prev_outputs')
    vout = models.ForeignKey('TxOutput', on_delete=models.PROTECT, help_text="Output index from previous transaction")
    script_sig = models.TextField(blank=True, null=True)

    @property
    def tx_data(self):
        data = {'prev_tx': self.prev_tx.id, 'vout': self.vout.id}
        return data

    @property
    def tx_signed_data(self):
        if not self.script_sig:
            raise TypeError("Data is not signed")
        data = {'prev_tx': self.prev_tx, 'vout': self.vout, 'script_sig': self.script_sig}
        return data


class TxOutput(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, related_name='outputs')
    value = models.BigIntegerField()
    script_pub_key = models.TextField(help_text='the target wallet public key', db_index=True)
    spent = models.BooleanField(default=False)

    class Meta:
        indexes = [
            HashIndex(fields=['script_pub_key'])
        ]

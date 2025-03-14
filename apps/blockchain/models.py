from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django.db.models import IntegerChoices
from django.db.models import Sum

from apps.common.models import BaseModel, BaseManager


class TxStatusChoices(IntegerChoices):
    PENDING = 0, 'Pending'
    COMPLETED = 1, 'Completed'
    FAILED = 2, 'Failed'


class TxVersionChoices(IntegerChoices):
    V1 = 1, 'V1'


class Transaction(BaseModel):
    version = models.PositiveIntegerField(choices=TxVersionChoices.choices, default=TxVersionChoices.V1)
    status = models.PositiveIntegerField(choices=TxStatusChoices.choices, default=TxStatusChoices.PENDING)


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
        data = {'prev_tx': self.prev_tx.id, 'vout': self.vout.id, 'script_sig': self.script_sig}
        return data


class TxOutput(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, related_name='outputs')
    value = models.DecimalField(max_digits=30, decimal_places=10)
    script_pub_key = models.TextField(help_text='the target wallet public key', db_index=True)
    spent = models.BooleanField(default=False)

    class Meta:
        indexes = [
            HashIndex(fields=['script_pub_key'])
        ]


class FiatTransactionKinds(IntegerChoices):
    WITHDRAW = 0, 'withdraw'
    DEPOSIT = 1, 'deposit'


class FiatTxManager(BaseManager):
    def calc_account_balance(self, account_id):
        calc_result = self.filter(account_id=account_id, spent=False, status=TxStatusChoices.COMPLETED).aggregate(
            balance=Sum(output_field=models.DecimalField())
        )
        return float(calc_result['balance']) or 0


class FiatTransaction(BaseModel):
    """
    This model keeps track(logs) of exchanging cryptocurrency with fiat currency
    These transactions are executed by a 3rd-party service e.g. a payment gateway
    """
    objects = FiatTxManager()

    value = models.DecimalField(max_digits=30, decimal_places=10)
    account = models.ForeignKey('users.Account', on_delete=models.PROTECT, related_name='transactions', db_index=True)
    status = models.PositiveIntegerField(choices=TxStatusChoices.choices, default=TxStatusChoices.PENDING)
    metadata = models.JSONField(default=dict)
    tracking_code = models.TextField(blank=True, null=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, related_name='transactions', null=True,
                                       blank=True)
    kind = models.BooleanField(choices=FiatTransactionKinds.choices)
    spent = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status != FiatTransactionKinds.DEPOSIT and self.spent is not None:
            raise ValueError(f"only the DEPOSIT transactions can have self.spent attribute")
        return super().save(*args, **kwargs)

    class Meta:
        indexes = [
            HashIndex(fields=['tracking_code'])
        ]

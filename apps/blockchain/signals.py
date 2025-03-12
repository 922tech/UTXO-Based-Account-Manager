from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from apps.blockchain.models import Transaction, TxInput, TxOutput
from apps.blockchain.services import TxService
from apps.common.utils import run_once


@receiver(post_migrate)
@run_once()
def create_coinbase(sender, **kwargs):
    """
    Creates the coinbase if no transactions exist
    """
    if not Transaction.objects.first():
        TxService().create_coinbase_transaction()
        print("Coinbase created successfully")

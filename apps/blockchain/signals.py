from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from apps.blockchain.models import Transaction, TxInput, TxOutput
from apps.common.utils import run_once
from apps.users.models import Account


@receiver(post_migrate)
@run_once()
def create_coinbase(sender, **kwargs):
    """
    Creates the coinbase if no transactions exist
    """
    if not Transaction.objects.first():
        tx = Transaction.objects.create()
        TxInput(transaction_id=tx.id, vout=0, script_sig="CoinbaseTX").save()
        admin_account = Account.objects.get(uuid=settings.ADMIN_ACCOUNT_UUID)
        TxOutput(transaction_id=tx.id, value=settings.COINBASE_REWARD, script_pub_key=admin_account.public_key).save()
        print("Coinbase created successfully")

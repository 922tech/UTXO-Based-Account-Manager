from celery import shared_task

from apps.blockchain.models import FiatTransaction
from apps.blockchain.services import TxService


@shared_task(bind=True, name='apps.blockchain.tasks.get_fiat_balance')
def get_fiat_balance(self, account_id: int) -> float:
    return FiatTransaction.objects.get_fiat_balance(account_id)


@shared_task(bind=True, name='apps.blockchain.tasks.get_crypto_balance')
def get_crypto_balance(self, public_key: int) -> float:
    return TxService.get_public_key_balance(public_key)

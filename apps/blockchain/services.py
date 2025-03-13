"""
This module wraps the business logic of the app obeying the
'service layer pattern' https://martinfowler.com/eaaCatalog/serviceLayer.html
"""
from django.conf import settings
from django.db.models import Sum
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from typing import Sequence

from apps.blockchain.models import TxInput, TxOutput, Transaction, TxStatusChoices, FiatTransaction, \
    FiatTransactionKinds
from apps.common.crypto import DigitalSigner
from apps.users.models import Account


class PaymentGatewayService:
    """
    This class is only a mock for payment gateway logic
    """

    def __init__(self, fiat_tx: FiatTransaction = None):
        self.fiat_tx = fiat_tx

    def verify_with_data(self, data):
        self.fiat_tx.status = TxStatusChoices.COMPLETED
        self.fiat_tx.metadata = data
        self.fiat_tx.save()
        return True

    def request(self):
        self.fiat_tx.save()
        return 'http://some-gateway.com/<token>'

    def charge_account(self, value, crypto_transaction_id):
        # self.fiat_tx.account.bank_account
        FiatTransaction(account=Account.objects.admin_account(),
                        value=value,
                        kind=FiatTransactionKinds.WITHDRAW,
                        transaction=crypto_transaction_id,
                        status=TxStatusChoices.COMPLETED).save()
        return True


class TxService:
    """
    This class wraps all the logic of validation of transactions
    """

    def __init__(self, transaction: Transaction = None, inputs: list[TxInput] = None, outputs: list[TxOutput] = None):
        self.inputs = inputs
        self.outputs = outputs
        self.tx = transaction
        self.utxos = TxOutput.objects.none()
        if not self.tx:
            self.tx = Transaction()

    @staticmethod
    def sign_tx(tx_input: TxInput, private_key, public_key) -> TxInput:
        signer = DigitalSigner(private_key_hex=private_key, public_key_hex=public_key)
        tx_input.script_sig = signer.sign(tx_input.tx_data)
        return tx_input

    @staticmethod
    def verify_input(tx_input: TxInput, public_key: str) -> bool:
        signer = DigitalSigner(public_key_hex=public_key)
        return signer.verify(tx_input.tx_data, tx_input.script_sig)

    def validate_transaction(self):
        sum_utxo_values = 0
        if not all([self.inputs, self.outputs]):
            raise TypeError("All inputs and outputs must be provided")

        for tx_input in self.inputs:
            utxos = TxOutput.objects.filter(transaction_id=tx_input.prev_tx_id, id=tx_input.vout_id, spent=False)
            if not utxos:  # check if such UTXOs exist in the first place
                raise ValidationError(
                    _("No unspent output with given previous transaction id and transaction output id"))
            for utxo in utxos:
                sum_utxo_values += utxo.value  # collect the values of UTXOs
                # verify the signature using previous outputs and the current script_sig
                if not self.verify_input(tx_input, utxo.script_pub_key):
                    raise ValidationError(_("Signature is not valid. Transaction aborted"))
            self.utxos = self.utxos.union(utxos)
        if not self.check_tx_value(sum_utxo_values):  # check the values
            raise ValidationError(_("No unspent output with given previous transaction id and transaction output id"))

    def check_tx_value(self, sum_utxo_values: int | float) -> bool:
        """
        Checks if the transaction's values match the balance of account
        """
        return sum_utxo_values == sum(output.value for output in self.outputs)

    def set_transaction_on(self, tx_seq: Sequence[TxInput | TxOutput]):
        for tx in tx_seq:
            tx.transaction = self.tx

    def spend_utxos(self):
        self.validate_transaction()
        try:
            with atomic():
                self.tx.status = TxStatusChoices.COMPLETED
                self.tx.save()
                self.set_transaction_on(self.outputs)
                self.set_transaction_on(self.inputs)

                self.utxos.select_for_update()  # lock the rows to prevent race-condition
                utxo_ids = [utxo.id for utxo in self.utxos]
                # NOTE: this is due to impossibility of updating a union query
                TxOutput.objects.filter(id__in=utxo_ids).update(spent=True)
                TxOutput.objects.bulk_create(self.outputs, batch_size=20)
        except Exception as e:
            # fail the transaction on error
            # TODO: log the unforeseen error
            self.tx.status = TxStatusChoices.FAILED
            self.tx.save()
            raise

    @staticmethod
    def get_public_key_balance(public_key):
        return TxOutput.objects.filter(script_pub_key=public_key, spent=False).aggregate(Sum('value')).get('value__sum')

    @atomic()
    def create_coinbase_transaction(self):
        """
        Coinbase transaction is a transaction that only has outputs and lacks inputs
        """
        admin_account = Account.objects.admin_account()
        self.tx.save()
        TxOutput(transaction=self.tx, value=settings.COINBASE_REWARD, script_pub_key=admin_account.public_key).save()

    @staticmethod
    def get_admin_account_utxo() -> TxOutput:
        # TODO: get the admin utxos for a given value using SUM window function
        admin_public_key = Account.objects.admin_account().public_key
        return TxOutput.objects.filter(script_pub_key=admin_public_key, spent=False).order_by('id').last()


class ExchangeService:

    def __init__(self, fiat_tx: FiatTransaction):
        self.fiat_tx = fiat_tx

    @staticmethod
    def get_exchange_rate() -> float:
        # This mocks getting the exchange rate from the market: fiat/crypto
        return 1000.0

    @classmethod
    def crypto_to_fiat(cls, crypto_value: float) -> float:
        return crypto_value * cls.get_exchange_rate()

    @classmethod
    def fiat_to_crypto(cls, fiat_value: float) -> float:
        return fiat_value / cls.get_exchange_rate()

    def buy_crypto(self, public_key: str) -> None:
        """
        crypto_value: value to buy
        public_key: public key of buyer's account
        """
        self._check_is_complete()
        if self.fiat_tx.kind != FiatTransactionKinds.DEPOSIT:
            raise ValueError("Transaction kind is not DEPOSIT!")
        crypto_value = self.fiat_to_crypto(float(self.fiat_tx.value))
        admin_utxo = TxService.get_admin_account_utxo()
        admin_account = Account.objects.admin_account()
        admin_account.decrypt_private_key()
        tx_input = TxInput(vout=admin_utxo.id, prev_tx=admin_utxo.transaction)
        change_value = admin_utxo.value - crypto_value
        signed_tx_input = TxService.sign_tx(tx_input, admin_utxo.script_pub_key, admin_account.decrypt_private_key())
        inputs = [signed_tx_input]
        if change_value < 0:
            raise ValidationError(_("Requested amount is too high"))

        account_output = TxOutput(value=crypto_value, script_pub_key=public_key)
        change = TxOutput(value=change_value, script_pub_key=admin_utxo.script_pub_key)
        tx_service = TxService(inputs=inputs, outputs=[change, account_output])
        # TODO: implement join coin operation and make it a periodic task
        self._finalize_exchange(tx_service)

    def _finalize_exchange(self, tx_service) -> None:
        with atomic():
            tx_service.spend_utxos()
            self.fiat_tx.transaction = tx_service.tx
            self.fiat_tx.save()

    def sell_crypto(self, tx_service: TxService) -> None:
        """
        selling crypto is just like spending with NEW_UTXO.public_key = admin_public_key
        call this once the payment gatewat transaction completed
        """
        self._check_is_complete()
        if self.fiat_tx.kind != FiatTransactionKinds.WITHDRAW:
            raise ValueError("Transaction kind is not WITHDRAW!")
        self._finalize_exchange(tx_service)
        with atomic():
            tx_service.spend_utxos()
            admin_public_key = Account.objects.admin_account().public_key
            sold_crypto = sum(
                o.value for o in filter(lambda x: x.script_pub_key == admin_public_key, tx_service.outputs))
            sold_crypto_fiat = self.crypto_to_fiat(sold_crypto)
            PaymentGatewayService(self.fiat_tx).charge_account(sold_crypto_fiat, tx_service.tx.id)

    def _check_is_complete(self):
        if self.fiat_tx.status != TxStatusChoices.COMPLETED:
            raise ValueError("Transaction is not complete")

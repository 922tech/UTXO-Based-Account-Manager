"""
This module wraps the business logic of the app obeying the
'service layer pattern' https://martinfowler.com/eaaCatalog/serviceLayer.html
"""
from django.conf import settings
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.blockchain.models import TxInput, TxOutput, Transaction
from apps.common.crypto import DigitalSigner
from apps.users.models import Account


class TxService:
    """
    This class wraps all the logic of validation of transactions
    """

    def __init__(self, transaction: Transaction = None, inputs: list[TxInput] = None, outputs: list[TxOutput] = None):
        self.inputs = inputs
        self.outputs = outputs
        self.tx = transaction
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
        # breakpoint()
        return signer.verify(tx_input.tx_data, tx_input.script_sig)

    def validate_vouts(self):
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
                print(utxo.script_pub_key, tx_input.script_sig)
                if not self.verify_input(tx_input, utxo.script_pub_key):
                    raise ValidationError(_("Signature is not valid. Transaction aborted"))

        if not self.check_tx_value(sum_utxo_values):  # check the values
            raise ValidationError(_("No unspent output with given previous transaction id and transaction output id"))

    def check_tx_value(self, sum_utxo_values: int | float) -> bool:
        """
        Checks if the transaction's values match the balance of account
        """
        return sum_utxo_values == sum(output.value for output in self.outputs)

    def create_utxo(self, ):
        pass

    @atomic()
    def create_coinbase_transaction(self):
        """
        Coinbase transaction is a transaction that only has outputs and lacks inputs
        """
        admin_account = Account.objects.get(uuid=settings.ADMIN_ACCOUNT_UUID)
        self.tx.save()
        TxOutput(transaction=self.tx, value=settings.COINBASE_REWARD, script_pub_key=admin_account.public_key).save()

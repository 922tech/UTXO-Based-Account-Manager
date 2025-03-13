from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.blockchain.models import Transaction, TxInput, TxOutput
from apps.blockchain.services import TxService
from apps.common.crypto import DigitalSigner
from apps.common.tests import BaseTestCase
from apps.users.models import Account


class TxServiceTestCase(BaseTestCase):
    def setUp(self):
        self.admin_account = Account.objects.get(uuid=settings.ADMIN_ACCOUNT_UUID)
        # Retrieve the coinbase transaction
        self.coinbase_tx = Transaction.objects.filter(outputs__script_pub_key=self.admin_account.public_key).first()
        self.assertIsNotNone(self.coinbase_tx, "Admin account must have a coinbase transaction")

        # Retrieve the UTXO from the coinbase transaction
        self.utxo = TxOutput.objects.filter(transaction=self.coinbase_tx, spent=False).first()
        self.assertIsNotNone(self.utxo, "Coinbase transaction must have an unspent output")

        self.tx_output = TxOutput(value=self.utxo.value, script_pub_key=self.admin_account.public_key)

        self.private_key = self.admin_account.decrypt_private_key()
        self.public_key = self.admin_account.public_key
        self.signer = DigitalSigner(public_key_hex=self.public_key, private_key_hex=self.private_key)

        # Create a new transaction input using the UTXO
        self.tx_input = TxInput(prev_tx_id=self.utxo.transaction.id, vout_id=self.utxo.id,
                                transaction_id=self.coinbase_tx.id)
        # sing the input to imitate a real input
        TxService.sign_tx(self.tx_input, self.private_key, self.public_key).save()
        self.tx_service = TxService(inputs=[self.tx_input], outputs=[self.tx_output])

    def test_sign_and_verify_tx(self):
        # Sign the transaction input
        tx_input = TxInput(prev_tx_id=self.utxo.transaction.id, vout_id=self.utxo.id,
                           transaction_id=self.coinbase_tx.id)
        tx_input.save()
        signed_input = self.tx_service.sign_tx(tx_input, self.private_key, self.public_key)
        self.assertIsNotNone(signed_input.script_sig, "Transaction input must be signed")

        # Verify the transaction input
        is_valid = self.tx_service.verify_input(signed_input, self.public_key)
        self.assertTrue(is_valid, "Signed transaction input must be valid")
        tx_input.delete()

    def test_validate_vouts(self):
        # Ensure validation does not raise an error
        try:
            self.tx_service.validate_transaction()
        except ValidationError:
            self.fail("validate_vouts should pass with correct inputs")

    def test_check_tx_value(self):
        # Check if transaction value matches the sum of outputs
        self.assertTrue(
            self.tx_service.check_tx_value(self.utxo.value),
            "Transaction value check should pass"
        )

    def test_spend(self):
        self.tx_service.spend_utxos()
        utxo_ids = [u.id for u in self.tx_service.utxos]
        self.assertTrue(all(TxOutput.objects.filter(id__in=utxo_ids).values_list('spent', flat=True)))

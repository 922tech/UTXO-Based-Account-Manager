from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blockchain.models import Transaction, TxInput, TxOutput, FiatTransaction, FiatTransactionKinds
from apps.blockchain.serializers import TxSerializer
from apps.blockchain.services import TxService, PaymentGatewayService, ExchangeService
from apps.common.views import BaseViewSet


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TxSerializer

    def get_tx_service(self):
        data, _ = self.get_validated_data(get_serializer=True, raise_exception=True)
        inputs = [TxInput(**input_data) for input_data in data['inputs']]
        outputs = [TxOutput(**input_data) for input_data in data['outputs']]
        tx_service = TxService(inputs=inputs, outputs=outputs)
        return tx_service

    def create(self, request, *args, **kwargs):
        """
        This method implements the view logic for transferring UTXOs among accounts
        """
        tx_service = self.get_tx_service()
        tx_service.spend_utxos()
        response_data = request.data
        response_data.update({'transaction': tx_service.tx.id})
        return Response(status=status.HTTP_201_CREATED, data=request.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def crypto_balance(self, request, *args, **kwargs):
        return TxService.get_public_key_balance(request.user.account.public_key)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def fiat_balance(self, request, *args, **kwargs): # Incomplete
        pass

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], serializer_class=TxSerializer)
    def withdraw(self, request, *args, **kwargs): # Incomplete
        """Converts UTXO to Fiat"""
        tx_service = self.get_tx_service()
        exchange_service = ExchangeService(FiatTransaction(account=request.user.account.id))
        exchange_service.sell_crypto(tx_service.tx)
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def deposit(self, request, *args, **kwargs):  # Incomplete
        """Converts Fiat to UTXO"""
        pg_service = PaymentGatewayService(FiatTransaction(account=request.user.account.id))
        link = pg_service.request()
        return Response(data={'url': link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def payment_gateway_webhook(self, request, *args, **kwargs):  # Incomplete
        # MOCK
        pg_service = PaymentGatewayService()
        pg_service.verify_with_data(request.data)
        if pg_service.fiat_tx.kind == FiatTransactionKinds.WITHDRAW:
            # TODO: you must find the account using the transaction metadata that the payment gateway sent you
            pass
            # ExchangeService(pg_service.fiat_tx).buy_crypto(account.public_key)
        return Response(status=status.HTTP_204_NO_CONTENT)

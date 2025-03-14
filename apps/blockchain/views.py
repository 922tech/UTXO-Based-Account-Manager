from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blockchain.models import Transaction, TxInput, TxOutput, FiatTransaction, FiatTransactionKinds
from apps.blockchain.serializers import TxSerializer, FiatTxSerializer, PaymentGwEventSerializer
from apps.blockchain.services import TxService, PaymentGatewayService, ExchangeService
from apps.common.pagination import LimitedLimitOffsetPagination
from apps.common.views import BaseViewSet


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TxSerializer
    # since list of the transactions must be cached on the client side, limit-offset pagination is the fittest
    pagination_class = LimitedLimitOffsetPagination
    def get_tx_service(self):
        data, _ = self.get_validated_data(raise_exception=True)
        inputs = [TxInput(**input_data) for input_data in data['inputs']]
        outputs = [TxOutput(**input_data) for input_data in data['outputs']]
        tx_service = TxService(inputs=inputs, outputs=outputs)
        return tx_service

    def get_queryset(self):
        if self.action in {'list', 'retrieve'}:
            return super().get_queryset().filter(outputs__script_pub_key=self.request.user.account.private_key)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        """
        This method implements the view logic for transferring UTXOs among accounts
        """
        tx_service = self.get_tx_service()
        tx_service.spend_utxos()
        response_data = request.data
        response_data.update({'transaction': tx_service.tx.id})
        return Response(status=status.HTTP_201_CREATED, data=request.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated], url_path="crypto-balance")
    def crypto_balance(self, request, *args, **kwargs):
        return Response(data={'balance': TxService.get_public_key_balance(request.user.account.public_key)})

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def fiat_balance(self, request, *args, **kwargs):  # Incomplete
        balance = FiatTransaction.objects.calc_account_balance(self.request.user.account.id)
        return Response(data={'balance': balance})

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], serializer_class=TxSerializer)
    def withdraw(self, request, *args, **kwargs):  # Incomplete
        """Converts UTXO to Fiat. This endpoint acts like spending UTXOs but the user gets paid afterward"""
        tx_service = self.get_tx_service()
        exchange_service = ExchangeService(FiatTransaction(account=request.user.account.id))
        exchange_service.sell_crypto(tx_service.tx, request.user.account)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], serializer_class=FiatTxSerializer)
    def deposit(self, request, *args, **kwargs):  # Incomplete
        """Request to deposit fiat into the network to exchange it with UTXO"""
        data = self.get_validated_data()
        pg_service = PaymentGatewayService(FiatTransaction(account=request.user.account.id, spent=False, **data))
        link = pg_service.request()
        return Response(data={'url': link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], serializer_class=PaymentGwEventSerializer)
    def payment_gateway_webhook(self, request, *args, **kwargs):  # Incomplete
        # MOCK
        data = self.get_validated_data()
        fiat_tx = FiatTransaction.objects.get(tracking_code=data['tracking_code'])
        pg_service = PaymentGatewayService(fiat_tx)
        pg_service.verify_with_data(data)
        if pg_service.fiat_tx.kind == FiatTransactionKinds.DEPOSIT:
            ExchangeService(pg_service.fiat_tx).buy_crypto(pg_service.fiat_tx.account.public_key)
        return Response(status=status.HTTP_204_NO_CONTENT)

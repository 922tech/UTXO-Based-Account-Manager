from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.blockchain.models import Transaction, TxInput, TxOutput, FiatTransaction
from apps.blockchain.serializers import TxSerializer
from apps.blockchain.services import TxService, PaymentGatewayService
from apps.common.views import BaseViewSet


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TxSerializer

    def create(self, request, *args, **kwargs):
        """
        This method implements the view logic for transferring UTXOs among accounts
        """
        data, _ = self.get_validated_data(get_serializer=True, raise_exception=True)
        inputs = [TxInput(**input_data) for input_data in data['inputs']]
        outputs = [TxOutput(**input_data) for input_data in data['outputs']]
        tx_service = TxService(inputs=inputs, outputs=outputs)
        tx_service.spend_utxos()
        response_data = request.data
        response_data.update({'transaction': tx_service.tx.id})
        return Response(status=status.HTTP_201_CREATED, data=request.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def crypto_balance(self, request, *args, **kwargs):
        pass

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def fiat_balance(self, request, *args, **kwargs):
        pass

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def history(self, request, *args, **kwargs):
        pass

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, *args, **kwargs):
        """Converts UTXO to Fiat"""
        pg_service = PaymentGatewayService(FiatTransaction(account=request.user.account.id))
        link = pg_service.request()
        return Response(data={'url': link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def deposit(self, request, *args, **kwargs):
        """Converts Fiat to UTXO"""
        pass

    @action(detail=False, methods=['POST'])
    def payment_gateway_webhook(self, request, *args, **kwargs):
        # MOCK
        pg_service = PaymentGatewayService()
        pg_service.verify_with_data(request.data)
        return Response()

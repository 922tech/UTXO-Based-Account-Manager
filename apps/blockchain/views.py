from rest_framework import mixins, status
from rest_framework.response import Response

from apps.blockchain.models import Transaction, TxInput, TxOutput
from apps.blockchain.serializers import TxSerializer
from apps.blockchain.services import TxService
from apps.common.views import BaseViewSet


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TxSerializer

    def create(self, request, *args, **kwargs):
        data, _ = self.get_validated_data(get_serializer=True, raise_exception=True)
        inputs = [TxInput(**input_data) for input_data in data['inputs']]
        outputs = [TxOutput(**input_data) for input_data in data['outputs']]
        tx_service = TxService(inputs=inputs, outputs=outputs)
        tx_service.spend_utxos()
        response_data = request.data
        response_data.update({'transaction': tx_service.tx.id})
        return Response(status=status.HTTP_201_CREATED, data=request.data)

from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from apps.blockchain.models import Transaction, TxInput, TxOutput, FiatTransaction
from apps.common.serializers import BaseModelSerializer, BaseSerializer


class TxListSerializer(ListSerializer):
    # TODO: implement this
    class Meta:
        pass


class TxInputSerializer(BaseModelSerializer):
    class Meta:
        model = TxInput
        exclude = ('transaction', 'is_active', 'is_deleted', 'updated_at')


class TxOutputSerializer(BaseModelSerializer):
    class Meta:
        model = TxOutput
        fields = ('value', 'script_pub_key')
        read_only_fields = ('spent',)


class TxSerializer(BaseModelSerializer):
    inputs = TxInputSerializer(many=True,)
    outputs = TxOutputSerializer(many=True,)

    class Meta:
        exclude = ('is_active', 'is_deleted', 'updated_at')
        model = Transaction
        read_only_fields = ('status', 'created_at',)


class FiatTxSerializer(BaseModelSerializer):
    class Meta:
        model = FiatTransaction
        fields = ('value', 'created_at', 'status', 'tracking_code', 'kind')
        read_only_fields = ('created_at', 'status', 'tracking_code', 'kind')
        write_once_fields = ('value',)


class PaymentGwEventSerializer(BaseSerializer):
    tracking_code = serializers.CharField()
    metadata = serializers.DictField()


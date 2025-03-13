from rest_framework.serializers import ListSerializer

from apps.blockchain.models import Transaction, TxInput, TxOutput
from apps.common.serializers import BaseModelSerializer


class PostListSerializer(ListSerializer):
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


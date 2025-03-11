from djoser.serializers import UserSerializer, UserCreateSerializer

from apps.common.serializers import BaseSerializer
from apps.users.models import Account


class AccountSerializer(UserSerializer):

    class Meta:
        model = Account
        fields = tuple(UserSerializer.Meta.fields) + ('private_key', 'public_key')
        read_only_fields = fields

    def to_representation(self, instance: Account):
        return super().to_representation(instance)

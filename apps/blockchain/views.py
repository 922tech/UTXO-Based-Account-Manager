from rest_framework import mixins

from apps.blockchain.models import Transaction
from apps.common.views import BaseViewSet


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    queryset = Transaction.objects.all()
    pass

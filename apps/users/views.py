from django.db import transaction
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status

from apps.common.views import BaseModelViewSet
from apps.users.models import Account
from apps.users.serializers import AccountSerializer


class UserViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super(UserViewSet, self).create(request, *args, **kwargs)
            if response.status_code == status.HTTP_201_CREATED:
                account = Account.objects.create(user_id=response.data['id'])
                account.decrypt_private_key()
                response.data.update({'private_key': account.private_key, 'public_key': account.public_key})
            return response


class AccountViewSet(BaseModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

from rest_framework_simplejwt.models import TokenUser as SimpleJWTTokenUser
from django.utils.functional import cached_property
from rest_framework_simplejwt.settings import api_settings
from uuid import UUID


class TokenUser(SimpleJWTTokenUser):
    @cached_property
    def id(self) -> UUID:
        return UUID(self.token[api_settings.USER_ID_CLAIM])

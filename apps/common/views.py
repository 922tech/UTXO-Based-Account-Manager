import h2o
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin, \
    DestroyModelMixin

from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from apps.common.utils import HealthCheck


class BaseViewSet(GenericViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return {
            'user': context['request'].user,
            'action': self.action,
            **context
        }

    def get_validated_data(self, raise_exception=False, get_serializer=False):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=raise_exception)
        if not get_serializer:
            return serializer.validated_data, serializer
        return serializer.validated_data, serializer


class BaseModelViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin,
                       BaseViewSet):
    pass


class BaseAPIView(APIView):
    pass


class CommonViewSet(BaseViewSet):
    @action(detail=False, url_path='health')
    def health(self, request):
        health = HealthCheck.all()
        return Response({'processor_server': health})


schema_view = get_schema_view(
    openapi.Info(
        title="Blockchain Service API ",
        default_version=settings.REST_FRAMEWORK['DEFAULT_VERSION'],
        description="API description",
    ),
    permission_classes=[permissions.AllowAny, ],
)

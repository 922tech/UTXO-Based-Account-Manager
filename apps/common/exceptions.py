from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class TooManyAttempts(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = 'too_many_attempts'


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('The external service is currently unavailable. Please try again later.')
    default_code = _('service_unavailable')


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('The external service is currently unavailable. Please try again later.')
    default_code = _('service_unavailable')



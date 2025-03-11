from rest_framework.permissions import BasePermission as DRFBasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class BasePermission(DRFBasePermission):
    pass


class IsAdmin(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        is_admin = bool(getattr(request, 'admin', False))
        return is_admin


class ReadOnly(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method in SAFE_METHODS

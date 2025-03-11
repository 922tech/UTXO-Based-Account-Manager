from typing import Any

from rest_framework.throttling import UserRateThrottle
from rest_framework.request import Request


class RouteBasedUserRateThrottle(UserRateThrottle):
    def get_cache_key(self, request: Request, view: Any) -> None | str:
        # type of `view` is RegisterView but cannot be annotated because 
        # rest_framework gets in trouble with it being import in here
        url = request.get_full_path()
        method = request.method
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': f"{url}_{method}_{ident}"
        }
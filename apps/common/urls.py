from django.conf import settings
from django.urls import path

from apps.common.views import schema_view

urlpatterns = [

]

if settings.DEBUG:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger.yaml/', schema_view.without_ui(cache_timeout=0), name='schema-yaml')
    ]

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from apps.common import urls as common_urls
from apps.blockchain import urls as blockchain_urls
from apps.users import urls as users_urls

api_patterns = [
    re_path(r'^(?P<version>[v1|v2]+)/', include(common_urls)),
    re_path(r'^(?P<version>[v1|v2]+)/', include(users_urls)),
    re_path(r'^(?P<version>[v1|v2]+)/', include(blockchain_urls)),
]

base_path = settings.API_PREFIX

urlpatterns = [
    re_path(f'{base_path}/', include(api_patterns)),
    path(f"{base_path}/admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]

"""
This module contains test reusable logics
"""
import inspect
import datetime
from uuid import uuid4

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from rest_framework.test import APITestCase, APIClient as DrfAPIClient
from rest_framework import status
from django.urls import resolve

error = 'File "%(filename)s", line %(lineno)d: Expected HTTP %(status_code)d OK but got %(response_status_code)d.\n\
         %(message)s\n Targeted view: %(view_address)s'


def create_jwt(uuid=uuid4(), username='user', exp=1):
    payload = {
        "user_id": uuid,
        "token_type": "access",
        "jti": uuid4().hex,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=exp)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


User = get_user_model()


class BaseTestCase(APITestCase):
    client = DrfAPIClient()
    client.force_authenticate(user=None)

    def tearDown(self):
        super().tearDown()
        for cache in caches.all(initialized_only=True):
            cache.clear()

    def force_login(self,
                    user=None,
                    uuid=None,
                    backend='django.contrib.auth.backends.ModelBackend') -> tuple[User, str]:
        if not user and not uuid:
            user, _ = User.objects.get_or_create(
                username='test_user', email='test@test.com',
            )
            uuid = '3f36bdb0-4dc1-430a-ad1e-f63f8af47366'
        if not uuid:
            uuid = str(uuid4())
        payload = {
            "user_id": uuid,
            "token_type": "access",
            "jti": uuid4().hex,
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client.force_login(user, backend=backend)
        return user, payload['user_id']

    def assertStatusEqual(self, response, status_code, message=''):
        if response.status_code != status_code:
            caller_frame = inspect.currentframe().f_back.f_back
            caller_info = inspect.getframeinfo(caller_frame)
            if not message:
                message = getattr(response, 'data', '')
            try:
                self.assertEqual(response.status_code, status_code)
            except AssertionError:
                view_info = self._get_view_path(response)
                raise AssertionError(
                    error % {
                        'filename': caller_info.filename,
                        'lineno': caller_info.lineno,
                        'status_code': status_code,
                        'response_status_code': response.status_code,
                        'message': message,
                        'view_address': view_info
                    }
                ) from None

    def _get_view_path(self, response):
        func = resolve(response.wsgi_request.path).func
        view = getattr(func, 'cls', func)
        return f'File: "{inspect.getfile(view)}", line {inspect.getsourcelines(view)[1]}, {view} '

    def assertSuccess(self, response=None, message=""):
        """
        Checks if the response status is 200.
        """
        self.assertStatusEqual(response, status.HTTP_200_OK, message)

    def assertCreateSuccess(self, response=None, message=""):
        self.assertStatusEqual(response, status.HTTP_201_CREATED, message)

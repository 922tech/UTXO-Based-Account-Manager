from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Account
from ..common.tests import BaseTestCase
from ..common.utils import reverse

User = get_user_model()


class UserViewSetTest(BaseTestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@test.test",
            "password": "securepassword123"
        }
        self.url = reverse('user-list')

    def test_create_user_and_account_success(self):
        """Test that a user and associated account are created successfully"""
        url = reverse('user-list')
        response = self.client.post(url, self.user_data)
        self.assertCreateSuccess(response)

        # Check if user was created
        user = User.objects.filter(username=self.user_data["username"]).first()
        self.assertIsNotNone(user)

        # Check if associated Account was created
        account = Account.objects.filter(user=user).first()
        self.assertIsNotNone(account)

        # Check if private/public keys are returned in response
        self.assertIn("private_key", response.data)
        self.assertIn("public_key", response.data)

    def test_create_duplicate_username_fails(self):
        """Test that creating a user with a duplicate username fails"""
        # Create a user first
        self.client.post(self.url, self.user_data)

        # Attempt to create a duplicate user
        response = self.client.post(self.url, self.user_data)
        self.assertStatusEqual(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

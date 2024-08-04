"""
Tests for the Auth Token API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase


PROTECTED_URL = reverse('church:municipality-list')


class TestAuthToken(APITestCase):
    """Test auth token Functionalities"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass',
            role=1
        )
        self.client = APIClient()

    def test_authenticate_success(self):
        """Test authenticating with valid credentials results in success."""
        res = self.client.post(
            '/api/token/',
            {'email': 'user@example.com', 'password': 'testpass'}
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn('role', res.data)
        self.assertEqual(res.data['role'], self.user.role)

        refresh_token = res.data.get('refresh')
        access_token = res.data.get('access')

        self.assertIsNotNone(refresh_token)
        self.assertIsNotNone(access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        res = self.client.get(PROTECTED_URL)

        self.assertEqual(res.status_code, 200)

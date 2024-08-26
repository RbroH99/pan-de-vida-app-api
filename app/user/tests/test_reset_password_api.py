"""
API test for reset password endpoints.
Generated with AI not written by developer.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
import jwt
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from user import views

UserModel = get_user_model()


class TestPasswordResetView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(name='testuser', email='test@example.com', password='password123')

    def test_password_reset_post_request(self):
        # Simular una solicitud POST
        url = reverse('user:password_reset')
        data = {"email": "test@example.com"}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Restablecer contraseña"

    def test_password_reset_post_request_invalid_email(self):
        # Simular una solicitud POST con un email inválido
        url = reverse('user:password_reset')
        data = {'email': 'invalid@example.com'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestResetPasswordView(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(name='testuser', email='test@example.com', password='password123')
        self.token = views.PasswordResetView.generate_password_reset_token(
            self,
            self.user
        )
        self.url = reverse('user:reset_password', args=[self.token])

    def test_reset_password_get_request_valid_token(self):
        # Simular una solicitud GET con un token válido
        response = self.client.get(self.url, format='json', data={'password': 'newpassword123'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_reset_password_get_request_invalid_token(self):
    #     # Simular una solicitud GET con un token inválido
    #     response = self.client.get('/api/reset-password/invalidtoken', content_type='application/json', data={'password': 'newpassword123'})

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_get_request_no_user_found(self):
        user = UserModel.objects.create(email="user2@example.com", password="password123")
        token = views.PasswordResetView.generate_password_reset_token(
            self,
            user
        )
        url = reverse('user:reset_password', args=[token])
        UserModel.delete(user)
        response = self.client.get(f'{url}', format='json', data={'password': 'newpassword123'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

"""
API tests for user creation and confirmation flows.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.contrib.auth import get_user_model
from user.serializers import (
    EmailConfirmationSerializer,
    EmailConfirmationMessageSerializer
)

UserModel = get_user_model()


class TestUserCreationView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = UserModel.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_user_success(self):
        """Test creating a user by admin should send confirmation email."""
        url = reverse('user:create-user')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'password123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirma tu cuenta', mail.outbox[0].subject)

    def test_create_user_without_email(self):
        """Test creating a user without an email should fail."""
        url = reverse('user:create-user')
        data = {
            'name': 'New User',
            'password': 'password123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class TestEmailConfirmationView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            email='user@example.com',
            password='password123',
            name='Test User'
        )
        # Generate a confirmation token
        self.token = EmailConfirmationMessageSerializer()\
            .generate_confirmation_token(self.user)

    def test_confirm_email_success(self):
        """Test confirming email with a valid token."""
        url = reverse('user:confirm-email')
        data = {'token': self.token}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_confirm_email_invalid_token(self):
        """Test confirming email with an invalid token."""
        url = reverse('user:confirm-email')
        data = {'token': 'invalidtoken'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestSetPasswordView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            email='user@example.com',
            password='password123',
            name='Test User'
        )
        self.token = EmailConfirmationMessageSerializer()\
            .generate_confirmation_token(self.user)
        EmailConfirmationSerializer().validate({"token": self.token})

    def test_set_password_success(self):
        """Test setting a new password after confirming email."""
        url = reverse('user:set-password')
        data = {
            'token': self.token,
            'password': 'newpassword123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_set_password_invalid_token(self):
        """Test setting a password with an invalid token."""
        url = reverse('user:set-password')
        data = {
            'token': 'invalidtoken',
            'password': 'newpassword123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_password_for_inactive_user(self):
        """Test setting a password for an inactive user."""
        self.user.is_active = False
        self.user.save()

        url = reverse('user:set-password')
        data = {
            'token': self.token,
            'password': 'newpassword123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

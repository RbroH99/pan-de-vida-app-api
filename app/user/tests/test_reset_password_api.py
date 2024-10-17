"""
API test for reset password endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from user import views, serializers

from app.settings import EMAIL_HOST_USER

UserModel = get_user_model()


class TestPasswordResetView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            name='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_password_reset_post_request(self):
        """Simulate Post Request."""
        url = reverse('user:password_reset')
        data = {"email": "test@example.com"}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Restablecer contraseña"

    def test_password_reset_post_request_invalid_email(self):
        """Simulate post request with invalid email token."""
        url = reverse('user:password_reset')
        data = {'email': 'invalid@example.com'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestResetPasswordView(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            name='testuser', email='test@example.com',
            password='password123')
        self.token = views.PasswordResetRequestSerializer\
            .generate_password_reset_token(
                self,
                self.user
            )
        self.url = reverse('user:reset_password')

    def test_reset_password_request_valid(self):
        """Simulate reset request for valid email"""
        response = self.client.post(
            reverse("user:password_reset"),
            format='json',
            data={'email': 'test@example.com'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = serializers.PasswordResetRequestSerializer\
            .generate_password_reset_token(
                self,
                self.user
            )
        url = reverse('user:reset_password')
        response = self.client.post(
            f'{url}',
            format='json',
            data={
                'password': 'newpassword123', "token": token
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_get_request_no_user_found(self):
        user = UserModel.objects.create(
            email="user2@example.com",
            password="password123")
        token = serializers.PasswordResetRequestSerializer\
            .generate_password_reset_token(
                self,
                user
            )
        url = reverse('user:reset_password')
        UserModel.delete(user)
        response = self.client.post(
            f'{url}',
            format='json',
            data={
                'password': 'newpassword123', "token": token
            }
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_smtp_connection(self):
        subject = 'Prueba de envío SMTP'
        message = 'Este es un mensaje de prueba.'
        email_from = EMAIL_HOST_USER,
        recipient_list = ['rbroh99@gmail.com']

        sent = mail.send_mail(
            subject,
            message,
            email_from,
            recipient_list,
            fail_silently=False
        )

        assert isinstance(sent, int) and sent > 0, "No se pudo enviar el email"

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.http import HttpRequest

from core.admin import UserAdmin


User = get_user_model()


class TestUserAdminSaveForm(TestCase):

    def setUp(self):
        self.user_admin = UserAdmin(User, admin.site)
        self.request = HttpRequest()
        self.request.method = "POST"
        self.request.POST = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'name': 'Test User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'role': 1,
        }

    def test_create_regular_user(self):
        response = self.user_admin.save_form(self.request, None, False)
        self.assertTrue(isinstance(response, User))
        self.assertEqual(response.email, 'test@example.com')

    def test_create_superuser(self):
        self.request.POST['is_superuser'] = True
        response = self.user_admin.save_form(self.request, None, False)
        self.assertTrue(isinstance(response, User))
        self.assertTrue(response.is_superuser)

    def test_update_user_role(self):
        user = User.objects.create_user(
            email='update@example.com',
            password='updatepass123',
            name='Update User',
            role=1
        )
        self.request.POST['email'] = 'updated@example.com'
        self.request.POST['name'] = 'Updated User'
        self.request.POST['role'] = 2
        self.user_admin.save_form(self.request, user, True)
        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.name, 'Updated User')
        self.assertEqual(updated_user.role, 2)

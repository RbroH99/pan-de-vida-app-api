"""
Test for the models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import MedClass

UserProfile = get_user_model()

class ModelTests(TestCase):
    """Test models."""

    def test_user_profile(self):
        """Test creating user profile in the API."""
        email = 'userprofile@example.com'
        user = UserProfile.objects.create_user(email=email)

        self.assertEqual(str(user), email)


    def test_create_medclass(self):
        """Test creating medclass"""
        medclass = MedClass.objects.create(name="Analgésico")

        self.assertEqual(str(medclass), "Analgésico")

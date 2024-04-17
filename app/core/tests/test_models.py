"""
Test for the models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import (
    MedClass,
    MedicinePresentation,
    Medicine
)

UserProfile = get_user_model()

class ModelTests(TestCase):
    """Test models."""

    def test_user_profile(self):
        """Test creating user profile in the API."""
        email = 'userprofile@example.com'
        id = 1
        user = UserProfile.objects.create_user(id=id, email=email)

        self.assertEqual(str(user), email)


    def test_create_medclass(self):
        """Test creating medclass"""
        medclass = MedClass.objects.create(name="Analgésico")

        self.assertEqual(str(medclass), "Analgésico")

    def test_create_medicine_presentation(self):
        """Test creating medicine presentation instance in the DB."""
        medpres = MedicinePresentation.objects.create(name="Óvulo")

        self.assertEqual(str(medpres), medpres.name)

    def test_create_medicine(self):
        """Test creating a medicine object in the DB."""
        medicine = Medicine.objects.create(name="Aspirina")

        self.assertEqual(str(medicine),
                         f'Name: {medicine.name}, Batch: {medicine.batch}')

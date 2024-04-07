"""
Test for the models.
"""
from django.test import TestCase

from core.models import MedClass


class ModelTests(TestCase):
    """Test models."""

    def test_create_medclass(self):
        """Test creating medclass"""
        medclass = MedClass.objects.create(name="Analgésico")

        self.assertEqual(str(medclass), "Analgésico")

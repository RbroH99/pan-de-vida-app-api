"""
Tests for the medicine classification API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    MedClass,
)

MEDCLASS_URL = reverse('medicine:medclass-list')


def detail_url(medclass_id):
    """Create and return a medicine classification detail URL."""
    return reverse('medicine:medclass-detail', args=[medclass_id])


class PublicMedicineClassificationAPITests(TestCase):
    """Tests for the anonymous medicine classification API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_medclass_list_error(self):
        """Test unauthenticated medclass-list fails."""
        res = self.client.get(MEDCLASS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_medclass_get_error(self):
        """Test unauthenticated getting medclass results in error."""
        medclass = MedClass.objects.create(name="Analgésico")

        url = detail_url(medclass.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(medclass, res.data)

    def test_anonymous_medclass_post_error(self):
        """Test unauthenticated post to medclass results in error."""
        payload = {"name": "Antiestamínico"}
        res = self.client.post(MEDCLASS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("name", res.data)

    def test_anonymous_medclass_update(self):
        """Test anonymous update request to medclass API fails."""
        medclass = MedClass.objects.create(name="Antiestamíninico")

        payload = {"name": "Analgésico"}
        url = detail_url(medclass.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        medclass.refresh_from_db()
        self.assertNotEqual(medclass.name, payload["name"])


class PrivateMedicineClassificationAPITests(TestCase):
    """Tests for the authenticated medicine classification API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9999,
            email="user2@example.com",
            password="testpass123",
            name="Test User",
            role=1,
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_medclass_list(self):
        """Test authenticated medclass-list success."""
        res = self.client.get(MEDCLASS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_medclass_get(self):
        """Test authenticated getting medclass detail success."""
        medclass = MedClass.objects.create(name="Analgésico")

        url = detail_url(medclass.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(medclass.name, res.data['name'])

    def test_medclass_post(self):
        """Test authenticated post to medclass success."""
        payload = {"name": "Antiestamínico"}
        res = self.client.post(MEDCLASS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("name", res.data)

    def test_medclass_update(self):
        """Test authenticated update request to medclass API."""
        medclass = MedClass.objects.create(name="Antiestamíminico")

        payload = {"name": "Analgésico"}
        url = detail_url(medclass.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        medclass.refresh_from_db()
        self.assertEqual(medclass.name, payload["name"])

    def test_medclass_delete(self):
        """Test authenticated can delete a medicine classification."""
        existing_medclass = MedClass.objects.create(name="Antiparasitario")

        url = detail_url(existing_medclass.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(existing_medclass, MedClass.objects.all())

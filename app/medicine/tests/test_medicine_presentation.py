"""
Tests for the medicine presentation API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    MedicinePresentation,
)

MEDPRES_URL = reverse('medicine:medicinepresentation-list')


def detail_url(medicine_presentation_id):
    """Create and return a medicine presentation detail URL."""
    return reverse('medicine:medicinepresentation-detail',
                   args=[medicine_presentation_id])


class PublicMedicinePresentationAPITests(TestCase):
    """Tests for the anonymous medicine presentation API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_medicinepresentation_list_error(self):
        """Test unauthenticated medicinepresentation-list fails."""
        res = self.client.get(MEDPRES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_medicinepresentation_get_error(self):
        """Test unauthenticated getting medicinepresentation forbidden."""
        medicinepresentation = \
            MedicinePresentation.objects.create(name="Analgésico")

        url = detail_url(medicinepresentation.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(medicinepresentation, res.data)

    def test_anonymous_medicinepresentation_post_error(self):
        """Test unauthenticated post to medicinepresentation forbidden."""
        payload = {"name": "Antiestamínico"}
        res = self.client.post(MEDPRES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("name", res.data)

    def test_anonymous_medicinepresentation_update(self):
        """Test anonymous update request to medicinepresentation API fails."""
        medicinepresentation = \
            MedicinePresentation.objects.create(name="Óvulo")

        payload = {"name": "Supositorio"}
        url = detail_url(medicinepresentation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        medicinepresentation.refresh_from_db()
        self.assertNotEqual(medicinepresentation.name, payload["name"])


class PrivateMedicinePresentationAPITests(TestCase):
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

    def test_medicinepresentation_list(self):
        """Test authenticated medicinepresentation-list success."""
        res = self.client.get(MEDPRES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_medicinepresentation_get(self):
        """Test authenticated getting medicinepresentation detail success."""
        medicinepresentation = \
            MedicinePresentation.objects.create(name="Analgésico")

        url = detail_url(medicinepresentation.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(medicinepresentation.name, res.data['name'])

    def test_medicinepresentation_post(self):
        """Test authenticated post to medicinepresentation success."""
        payload = {"name": "Antiestamínico"}
        res = self.client.post(MEDPRES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("name", res.data)

    def test_medicinepresentation_update(self):
        """Test authenticated update request to medicinepresentation API."""
        medicinepresentation = \
            MedicinePresentation.objects.create(name="Antiestamíminico")

        payload = {"name": "Analgésico"}
        url = detail_url(medicinepresentation.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        medicinepresentation.refresh_from_db()
        self.assertEqual(medicinepresentation.name, payload["name"])

    def test_medicinepresentation_delete(self):
        """Test authenticated can delete a medicine presentation."""
        existing_medicinepresentation = \
            MedicinePresentation.objects.create(name="Antiparasitario")

        url = detail_url(existing_medicinepresentation.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(existing_medicinepresentation,
                         MedicinePresentation.objects.all())

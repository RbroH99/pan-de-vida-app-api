"""
Tests for the medicine API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Medicine,
)

from medicine.serializers import MedicineSerializer

MEDICINE_URL = reverse('medicine:medicine-list')


def detail_url(medicine_id):
    """Create and return a medicine detail URL."""
    return reverse('medicine:medicine-detail', args=[medicine_id])


class PublicMedicineAPITests(TestCase):
    """Unauthenticated requests to the medicine API."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_medicine_list(self):
        """Test unauthenticated request to medicine API results in error."""
        res = self.client.get(MEDICINE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_medicine_detail(self):
        """Test anonymous request to medicine details results in error."""
        medicine = Medicine.objects.create(name='Aspirine')

        url = detail_url(medicine.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(medicine.name, res.data)

    def test_anonymous_medicine_create(self):
        """Test anonymously create a medicine instance fails."""
        payload = {
            "name": "Dipirone",
            "batch": "72T4532"
        }
        res = self.client.post(MEDICINE_URL, payload, format='json')

        self. assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(payload['name'], res.data)

    def test_anonymous_medicine_update(self):
        """Test anoymously update medicine instance reults in error."""
        medicine = Medicine.objects.create(name="Loratadine")

        payload = {
            "name": "Dipirone",
            "batch": "35E21"
        }
        url = detail_url(medicine.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        medicine.refresh_from_db()
        self.assertNotEqual(medicine.name, payload["name"])
        self.assertIsNone(medicine.batch)


class PrivateMedicineAPITests(TestCase):
    """Test for the private API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9998,
            email='user@example.com'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_staff_create_medicine(self):
        """Test staff user creating medicine instance success."""
        payload = {
            "name": "Dipirone",
            "batch": "7T43E2"
        }
        res = self.client.post(MEDICINE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_staff_list_medicine(self):
        """Test staff user listing medicine instances success."""
        Medicine.objects.create(name="Medicine1")
        Medicine.objects.create(name="Medicine2")

        res = self.client.get(MEDICINE_URL)

        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_staff_delete_medicine(self):
        """Test staff user deleting medicine instance success."""
        medicine = Medicine.objects.create(name="Medicine Name")

        url = detail_url(medicine.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_update_medicine(self):
        """Test staff user updating medicine instance success."""
        medicine = Medicine.objects.create(name="Medicine Name")

        url = detail_url(medicine.id)
        payload = {"name": "New Name"}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        medicine.refresh_from_db()
        self.assertEqual(medicine.name, payload["name"])

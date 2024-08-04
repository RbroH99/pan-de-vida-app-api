"""
Tests for the medicine API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from unittest.mock import Mock

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Medicine,
    MedClass,
    MedicinePresentation,
)

from medicine.serializers import MedicineSerializer

MEDICINE_URL = reverse('medicine:medicine-list')


def detail_url(medicine_id):
    """Create and return a medicine detail URL."""
    return reverse('medicine:medicine-detail', args=[medicine_id])


def create_medicine(
        medicine_name="Test Name",
        med_class_name="Classification Name",
        presentation_name='Presentation Name',
        measurement=200
):

    classification = MedClass.objects.create(name=med_class_name)
    presentation = MedicinePresentation.objects.create(
        name=presentation_name
    )
    return Medicine.objects.create(
        name=medicine_name,
        classification=classification,
        presentation=presentation,
        measurement=measurement
    )


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
        }
        res = self.client.post(MEDICINE_URL, payload, format='json')

        self. assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(payload['name'], res.data)

    def test_anonymous_medicine_update(self):
        """Test anoymously update medicine instance reults in error."""
        medicine = Medicine.objects.create(name="Loratadine")

        payload = {
            "name": "Dipirone",
        }
        url = detail_url(medicine.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        medicine.refresh_from_db()
        self.assertNotEqual(medicine.name, payload["name"])


class PrivateMedicineAPITests(TestCase):
    """Test for the private API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9998,
            email='user@example.com',
            role=1
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_staff_create_medicine(self):
        """Test staff user creating medicine instance success."""
        payload = {
            "name": "Dipirone",
        }
        res = self.client.post(MEDICINE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_staff_list_medicine(self):
        """Test staff user listing medicine instances success."""
        Medicine.objects.create(name="Medicine1")
        Medicine.objects.create(name="Medicine2")

        res = self.client.get(MEDICINE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        request_mock = Mock()
        request_mock.user = self.user

        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True,
                                        context={'request': request_mock})
        self.assertEqual(serializer.data, res.json())

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

    def test_create_medicine_with_existing_classification_name(self):
        """Test existing classification is associated to medicine instance."""
        classification = MedClass.objects.create(name="Test classif")

        classification_dict = {
            "name": classification.name
        }

        payload = {
            "name": "Medicine Name",
            "classification": classification_dict,
        }

        res = self.client.post(MEDICINE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            classification.name, res.data["classification"]["name"]
        )

    def test_create_medicine_with_non_existing_classification_name(self):
        """Test new classification created on medicine creation."""

        classification_dict = {
            "name": "Non existing"
        }

        payload = {
            "name": "Medicine Name",
            "classification": classification_dict,
        }

        res = self.client.post(MEDICINE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            classification_dict["name"], res.data["classification"]["name"]
        )

    def test_create_medicine_with_existing_presentation_name(self):
        """Test existing classification is associated to medicine instance."""
        presentation = MedicinePresentation.objects.create(name="Test present")

        presentation_dict = {
            "name": presentation.name
        }

        payload = {
            "name": "Medicine Name",
            "presentation": presentation_dict,
        }

        res = self.client.post(MEDICINE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            presentation.name, res.data["presentation"]["name"]
        )

    def test_create_medicine_with_non_existing_presentation_name(self):
        """Test new presentation created on medicine creation."""

        presentation_dict = {
            "name": "Non existing"
        }

        payload = {
            "name": "Medicine Name",
            "presentation": presentation_dict,
        }

        res = self.client.post(MEDICINE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            presentation_dict["name"], res.data["presentation"]["name"]
        )


class PrivateFilteringAPITests(TestCase):
    """Test cases for the filtering and ordering in API responses."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9997,
            email='user@example.com',
            role=1
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.medicine1 = create_medicine(
            medicine_name="A Medicine",
            med_class_name="A Classification",
            presentation_name='A Presentation',
        )
        self.medicine2 = create_medicine(
            medicine_name="Z Medicine",
            med_class_name="Z Classification",
            presentation_name='Z Presentation',
            measurement=250
        )

    def test_ordering_filter(self):
        """Test ordering filter works correctly."""
        res = self.client.get(f"{MEDICINE_URL}?ordering=name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine1.id)
        self.assertEqual(res.data[-1]['id'], self.medicine2.id)

        res = self.client.get(f"{MEDICINE_URL}?ordering=-presentation__name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[-1]['id'], self.medicine1.id)
        self.assertEqual(res.data[0]['id'], self.medicine2.id)

        res = self.client.get(f"{MEDICINE_URL}?ordering=-measurement")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[-1]['id'], self.medicine1.id)
        self.assertEqual(res.data[0]['id'], self.medicine2.id)

    def test_search_filter(self):
        """Test search filter works as expected."""
        res = self.client.get(f"{MEDICINE_URL}?a")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine1.id)

        res = self.client.get(f"{MEDICINE_URL}?search=z")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine2.id)

    def test_fields_filter(self):
        """Test filter by fields works as expected."""
        res = self.client.get(f"{MEDICINE_URL}?name=A Medicine")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine1.id)

        res = self.client.get(
            f"{MEDICINE_URL}?presentation__name=Z Presentation"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine2.id)

        res = self.client.get(
            f"{MEDICINE_URL}?classification__name=A Classification"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.medicine1.id)


class RoleBasedAPITests(TestCase):
    """Test endpoint responses accordin to the user role."""

    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            id=9997,
            email='adminuser@example.com',
            role=1
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin_user)

        self.agent_user = get_user_model().objects.create_user(
            id=9996,
            email='agentuser@example.com',
            role=2
        )
        self.agent_client = APIClient()
        self.agent_client.force_authenticate(self.agent_user)

        self.donor_user = get_user_model().objects.create_user(
            id=9995,
            email='donoruser@example.com',
        )
        self.donor_client = APIClient()
        self.donor_client.force_authenticate(self.donor_user)

    def test_donor_cant_access_medicines(self):
        """Test donor user can't reach the medicine endpoints."""
        medicine = Medicine.objects.create(name="Medicine Name")
        url = detail_url(medicine.id)

        res = self.donor_client.get(MEDICINE_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.donor_client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.donor_client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.donor_client.patch(url, {"name": "New Name"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_quantity_if_user_is_agent(self):
        """Test quantity is not in the response if user is agent."""

        medicine = Medicine.objects.create(name="Medicine Name")

        url = detail_url(medicine.id)
        res = self.agent_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('quantity', res.data)

    def test_quantity_in_if_user_is_admin(self):
        """Test quantity is in the response if user is admin."""
        medicine = Medicine.objects.create(name="Medicine Name", quantity=2)

        url = detail_url(medicine.id)
        res = self.admin_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('quantity', res.data)

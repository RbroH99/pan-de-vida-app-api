"""
Tests for the meddic API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Contact,
    WorkingSite,
    Medic
)


MEDIC_URL = reverse('contact:medic-list')


def detail_url(medic_id):
    """Create and return a medic's detail URL."""
    return reverse('contact:medic-detail', args=[medic_id])


def create_medic(contact_name="John", spec="Pedriatician", wks="wks1"):
    """Create and return a new medic instance."""
    contact = Contact.objects.create(name=contact_name)
    workingsite = WorkingSite.objects.create(name=wks)
    medic = Medic.objects.create(
        contact=contact,
        workingsite=workingsite,
        specialty=spec
    )
    return medic


class PublicMedicAPITests(TestCase):
    """Tests for unauthenticated users trying to access Medic endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.medic_data = {
            'contact': {'name': 'John Doe'},
            'workingsite': {'name': 'Working Site 1'},
            'specialty': 'Cardiology'
        }

    def test_create_medic_unauthenticated(self):
        """Test unauthenticated cannot create a new Medic."""
        res = self.client.post(MEDIC_URL,
                               self.medic_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_medics_unauthenticated(self):
        """Test unauthenticated cannot list all Medics."""
        res = self.client.get(MEDIC_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_medic_unauthenticated(self):
        """Test unauthenticated cannot access the details of a Medic."""
        medic = create_medic()

        url = detail_url(medic.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_medic_unauthenticated(self):
        """Test unauthenticated cannot update a Medic."""
        medic = create_medic()

        payload = {
            'contact': {'name': 'Johana'},
            'workingsite': {'name': 'Working Site 3'},
            'specialty': 'Cardiology'
        }
        url = detail_url(medic.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        medic.refresh_from_db()
        self.assertNotEqual(medic.specialty, payload['specialty'])

    def test_delete_medic_unauthenticated(self):
        """Test unauthenticated cannot delete a Medic."""
        medic = create_medic()

        url = detail_url(medic.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMedicAPITest(TestCase):
    """
    Test cases for authenticated users trying to access Medic endpoints.
    """
    def setUp(self):
        """
        Set up the test environment for authenticated users.
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            id=999999,
            email='test@example.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        self.medic_data = {
            'contact': {'name': 'Jane Doe'},
            'workingsite': {'name': 'Working Site 2'},
            'specialty': 'Neurology'
        }

    def test_create_medic_authenticated(self):
        """
        Test that authenticated users can create a new Medic.
        """
        res = self.client.post(MEDIC_URL,
                               self.medic_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_medics_authenticated(self):
        """
        Test that authenticated users can list all Medics.
        """
        res = self.client.get(MEDIC_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_medic_authenticated(self):
        """
        Test that authenticated users can access the details of a Medic.
        """
        medic = create_medic()

        url = detail_url(medic.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_medic_authenticated(self):
        """
        Test that authenticated users can update a Medic.
        """
        medic = create_medic()

        url = detail_url(medic.id)
        res = self.client.patch(url, **self.medic_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_medic_authenticated(self):
        """
        Test that authenticated users can delete a Medic.
        """
        medic = create_medic()

        url = detail_url(medic.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

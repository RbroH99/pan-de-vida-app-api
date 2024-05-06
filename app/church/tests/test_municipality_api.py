"""
Tests for the Munincipality API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Municipality


MUNICIPALITY_URL = reverse('church:municipality-list')


def detail_url(municipality_id):
    """Create and return a municipality's detail URL."""
    return reverse('church:municipality-detail', args=[municipality_id])


def create_municipality(name="Vedado", province="HAB"):
    """Create and return a new municipality instance."""
    return Municipality.objects.create(name=name, province=province)


class PublicMunicipalityAPITests(TestCase):
    """Tests unauthenticated users trying to access municipality endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.municipality_data = {
            'name': 'Gibara',
            'province': 'HOL'
        }

    def test_create_municipality_unauthenticated(self):
        """Test unauthenticated cannot create a new municipality."""
        res = self.client.post(MUNICIPALITY_URL,
                               self.municipality_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_municipalities_unauthenticated(self):
        """Test unauthenticated cannot list all municipalities."""
        res = self.client.get(MUNICIPALITY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_municipality_unauthenticated(self):
        """Test unauthenticated cannot access the details of a municipality."""
        municipality = create_municipality()

        url = detail_url(municipality.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_municipality_unauthenticated(self):
        """Test unauthenticated cannot update a municipality."""
        municipality = create_municipality()

        url = detail_url(municipality.id)
        payload = {
            'name': 'New Havana',
            'province': 'MAL'
        }
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_municipality_unauthenticated(self):
        """Test unauthenticated cannot delete a municipality."""
        municipality = create_municipality()

        url = detail_url(municipality.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMunicipalityAPITest(TestCase):
    """
    Tests for authenticated users trying to access municipality endpoints.
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
        self.municipality_data = {
            'name': 'Vedado',
            'province': 'HAB'
        }

    def test_create_municipality_authenticated(self):
        """
        Test that authenticated users can create a new municipality.
        """
        res = self.client.post(MUNICIPALITY_URL,
                               self.municipality_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_municipalities_authenticated(self):
        """
        Test that authenticated users can list all municipalities.
        """
        res = self.client.get(MUNICIPALITY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_municipality_authenticated(self):
        """
        Test that authenticated users can access the details of a municipality.
        """
        municipality = create_municipality()

        url = detail_url(municipality.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_municipality_authenticated(self):
        """
        Test that authenticated users can update a municipality.
        """
        municipality = create_municipality()

        url = detail_url(municipality.id)
        payload = {
            'name': 'Varadero',
            'province': 'MTZ'
        }
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_municipality_authenticated(self):
        """
        Test that authenticated users can delete a municipality.
        """
        municipality = create_municipality()

        url = detail_url(municipality.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

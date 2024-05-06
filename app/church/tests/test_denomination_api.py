"""
Tests for the denomination API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Denomination


DENOMINATION_URL = reverse('church:denomination-list')


def detail_url(denomination_id):
    """Create and return a denomination's detail URL."""
    return reverse('church:denomination-detail', args=[denomination_id])


def create_denomination(name="Test Denomination"):
    """Create and return a new denomination instance."""
    denomination = Denomination.objects.create(name=name)
    return denomination


class PublicDenominationAPITests(TestCase):
    """Test unauthenticated users trying to access denomination endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.denomination_data = {
            'name': 'Test Denomination'
        }

    def test_create_denomination_unauthenticated(self):
        """Test unauthenticated cannot create a new denomination."""
        res = self.client.post(DENOMINATION_URL,
                               self.denomination_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_denominations_unauthenticated(self):
        """Test unauthenticated cannot list all denominations."""
        res = self.client.get(DENOMINATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_denomination_unauthenticated(self):
        """Test unauthenticated cannot access details of a denomination."""
        denomination = create_denomination()
        url = detail_url(denomination.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_denomination_unauthenticated(self):
        """Test unauthenticated cannot update a denomination."""
        denomination = create_denomination()
        payload = {'name': 'Updated Denomination'}
        url = detail_url(denomination.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        denomination.refresh_from_db()
        self.assertNotEqual(denomination.name, payload['name'])

    def test_delete_denomination_unauthenticated(self):
        """Test unauthenticated cannot delete a denomination."""
        denomination = create_denomination()
        url = detail_url(denomination.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDenominationAPITest(TestCase):
    """
    Test cases for authenticated users trying to access denomination endpoints.
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
        self.denomination_data = {
            'name': 'Test Denomination'
        }

    def test_create_denomination_authenticated(self):
        """
        Test that authenticated users can create a new denomination.
        """
        res = self.client.post(DENOMINATION_URL,
                               self.denomination_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_denominations_authenticated(self):
        """
        Test that authenticated users can list all denominations.
        """
        res = self.client.get(DENOMINATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_denomination_authenticated(self):
        """
        Test that authenticated users can access the details of a denomination.
        """
        denomination = create_denomination()
        url = detail_url(denomination.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_denomination_authenticated(self):
        """
        Test that authenticated users can update a denomination.
        """
        denomination = create_denomination()
        url = detail_url(denomination.id)
        res = self.client.patch(url, self.denomination_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_denomination_authenticated(self):
        """
        Test that authenticated users can delete a denomination.
        """
        denomination = create_denomination()
        url = detail_url(denomination.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

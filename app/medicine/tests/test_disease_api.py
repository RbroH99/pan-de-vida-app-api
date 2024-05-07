"""
Tests for the disease API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Disease


DISEASE_URL = reverse('medicine:disease-list')


def detail_url(disease_id):
    """Create and return a disease's detail URL."""
    return reverse('medicine:disease-detail', args=[disease_id])


def create_disease(name="Test Disease"):
    """Create and return a new disease instance."""
    disease = Disease.objects.create(name=name)
    return disease


class PublicDiseaseAPITests(TestCase):
    """Test unauthenticated users trying to access disease endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.disease_data = {
            'name': 'Test Disease'
        }

    def test_create_disease_unauthenticated(self):
        """Test unauthenticated cannot create a new disease."""
        res = self.client.post(DISEASE_URL,
                               self.disease_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_diseases_unauthenticated(self):
        """Test unauthenticated cannot list all diseases."""
        res = self.client.get(DISEASE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_disease_unauthenticated(self):
        """Test unauthenticated cannot access details of a disease."""
        disease = create_disease()
        url = detail_url(disease.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_disease_unauthenticated(self):
        """Test unauthenticated cannot update a disease."""
        disease = create_disease()
        payload = {'name': 'Updated Disease'}
        url = detail_url(disease.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        disease.refresh_from_db()
        self.assertNotEqual(disease.name, payload['name'])

    def test_delete_disease_unauthenticated(self):
        """Test unauthenticated cannot delete a disease."""
        disease = create_disease()
        url = detail_url(disease.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDiseaseAPITest(TestCase):
    """
    Test cases for authenticated users trying to access disease endpoints.
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
        self.disease_data = {
            'name': 'Test Disease'
        }

    def test_create_disease_authenticated(self):
        """
        Test that authenticated users can create a new disease.
        """
        res = self.client.post(DISEASE_URL,
                               self.disease_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_diseases_authenticated(self):
        """
        Test that authenticated users can list all diseases.
        """
        res = self.client.get(DISEASE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_disease_authenticated(self):
        """
        Test that authenticated users can access the details of a disease.
        """
        disease = create_disease()
        url = detail_url(disease.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_disease_authenticated(self):
        """
        Test that authenticated users can update a disease.
        """
        disease = create_disease()
        url = detail_url(disease.id)
        res = self.client.patch(url, self.disease_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_disease_authenticated(self):
        """
        Test that authenticated users can delete a disease.
        """
        disease = create_disease()
        url = detail_url(disease.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

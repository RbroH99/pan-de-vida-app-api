"""
Tests for de meddic API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Contact,
    Donor
)


DONOR_URL = reverse('contact:donor-list')


def detail_url(donor_id):
    """Create and return a donor's detail URL."""
    return reverse('contact:donor-detail', args=[donor_id])


def create_donor(contact_name="John", country="ESP", city="Madrid"):
    """Create and return a new donor instance."""
    contact = Contact.objects.create(name=contact_name)
    donor = Donor.objects.create(
        contact=contact,
        country=country,
        city=city
    )
    return donor


class PublicdonorAPITests(TestCase):
    """Tests for unauthenticated users trying to access donor endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.donor_data = {
            'contact': {'name': 'John Doe'},
            'country': {},
            'city': 'Florida'
        }

    def test_create_donor_unauthenticated(self):
        """Test unauthenticated cannot create a new donor."""
        res = self.client.post(DONOR_URL,
                               self.donor_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_donors_unauthenticated(self):
        """Test unauthenticated cannot list all donors."""
        res = self.client.get(DONOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_donor_unauthenticated(self):
        """Test unauthenticated cannot access the details of a donor."""
        donor = create_donor()

        url = detail_url(donor.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_donor_unauthenticated(self):
        """Test unauthenticated cannot update a donor."""
        donor = create_donor()

        payload = {
            'contact': {'name': 'Johana'},
            'city': 'Rome'
        }
        url = detail_url(donor.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        donor.refresh_from_db()
        self.assertNotEqual(donor.city, payload['city'])

    def test_delete_donor_unauthenticated(self):
        """Test unauthenticated cannot delete a donor."""
        donor = create_donor()

        url = detail_url(donor.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatedonorAPITest(TestCase):
    """
    Test cases for authenticated users trying to access donor endpoints.
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
        self.donor_data = {
            'contact': {'name': 'Jane Doe'},
            'city': 'Habana'
        }

    def test_create_donor_authenticated(self):
        """
        Test that authenticated users can create a new donor.
        """
        res = self.client.post(DONOR_URL,
                               self.donor_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_donors_authenticated(self):
        """
        Test that authenticated users can list all donors.
        """
        res = self.client.get(DONOR_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_donor_authenticated(self):
        """
        Test that authenticated users can access the details of a donor.
        """
        donor = create_donor()

        url = detail_url(donor.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_donor_authenticated(self):
        """
        Test that authenticated users can update a donor.
        """
        donor = create_donor()

        url = detail_url(donor.id)
        res = self.client.patch(url, **self.donor_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_donor_authenticated(self):
        """
        Test that authenticated users can delete a donor.
        """
        donor = create_donor()

        url = detail_url(donor.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_donor_with_country(self):
        """Test creating a donor with valid country."""
        payload = self.donor_data | {'country': 'US'}

        res = self.client.post(DONOR_URL, payload, format='json')

        self.assertEqual(res.data.country.code, "US")
        self.assertEqual(res.data.country.name, "United States")

    def test_create_donor_with_invalid_country(self):
        """Test create a donor with invalid country."""
        with self.assertRaises(ValueError):
            Donor.objects.create(name="John Doe", country="INVALID")

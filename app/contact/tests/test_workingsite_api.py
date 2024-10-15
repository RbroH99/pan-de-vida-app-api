"""
Tests for the medics working site API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import WorkingSite


WORKING_SITE_URL = reverse('contact:workingsite-list')


def detail_url(working_site_id):
    """Create and return a working-site's detail URL."""
    return reverse('contact:workingsite-detail', args=[working_site_id])


def create_user(id=99999, email="user@example.com"):
    """Creates and return a new user."""
    user = get_user_model().objects.create_user(
        id=id,
        email=email,
        password="testpass123",
        )

    return user


class PublicWorkingSiteAPITests(TestCase):
    """Tests unauthenticated users trying to access WorkingSite endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.working_site_data = {'name': 'Sitio de trabajo 1'}
        self.working_site = \
            WorkingSite.objects.create(**self.working_site_data)

    def test_create_working_site_unauthenticated(self):
        """Test unauthenticated cannot create a new WorkingSite."""
        url = WORKING_SITE_URL
        res = self.client.post(url, self.working_site_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_working_sites_unauthenticated(self):
        """Test unauthenticated cannot list all WorkingSites."""
        url = WORKING_SITE_URL
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_working_site_unauthenticated(self):
        """Test unauthenticated cannot access the details of a WorkingSite."""
        url = detail_url(self.working_site.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_working_site_unauthenticated(self):
        """Test unauthenticated cannot update a WorkingSite."""
        payload = {"name": "New Name"}
        url = detail_url(self.working_site.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.working_site.refresh_from_db()
        self.assertNotEqual(self.working_site.name, payload['name'])

    def test_delete_working_site_unauthenticated(self):
        """Test unauthenticated cannot delete a WorkingSite."""
        url = detail_url(self.working_site.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWorkingSiteAPITest(TestCase):
    """Tests authenticated users trying to access WorkingSite endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.working_site_data = {'name': 'Sitio de trabajo 2'}
        self.working_site = \
            WorkingSite.objects.create(**self.working_site_data)

    def test_create_working_site_authenticated(self):
        """Test authenticated users can create a new WorkingSite."""
        url = WORKING_SITE_URL
        res = self.client.post(url, self.working_site_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkingSite.objects.count(), 2)

    def test_list_working_sites_authenticated(self):
        """Test authenticated users can list all WorkingSites."""
        url = WORKING_SITE_URL
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_working_site_authenticated(self):
        """Test authenticated can access the details of a WorkingSite."""
        url = detail_url(self.working_site.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_working_site_authenticated(self):
        """Test authenticated users can update a WorkingSite."""
        payload = {"name": "New Name"}
        url = detail_url(self.working_site.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.working_site.refresh_from_db()
        self.assertEqual(self.working_site.name, payload['name'])

    def test_delete_working_site_authenticated(self):
        """Test that authenticated users can delete a WorkingSite."""
        url = detail_url(self.working_site.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

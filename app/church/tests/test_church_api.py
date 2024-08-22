"""
Tests for the Church API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from church import serializers

from core.models import (
    Denomination,
    Municipality,
    Church
)


CHURCH_URL = reverse('church:church-list')


def detail_url(church_id):
    """Create and return a church's detail URL."""
    return reverse('church:church-detail', args=[church_id])


def create_church(name="Test Church",
                  denomination_name="Test Denomination",
                  municipality_name="Test Municipality",
                  province="UNK"):
    """Create and return a new church instance."""
    denomination = Denomination.objects.create(name=denomination_name)
    municipality = Municipality.objects.create(name=municipality_name,
                                               province=province)
    church = Church.objects.create(
        name=name,
        denomination=denomination,
        municipality=municipality
    )
    return church


class PublicChurchAPITests(TestCase):
    """Tests for unauthenticated users trying to access church endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.church_data = {
            'name': 'Test Church',
            'denomination': {'name': 'Test Denomination'},
            'municipality': {'name': 'Test Municipality', 'province': 'UNK'}
        }

    def test_create_church_unauthenticated(self):
        """Test unauthenticated cannot create a new church."""
        res = self.client.post(CHURCH_URL, self.church_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_churches_unauthenticated(self):
        """Test unauthenticated cannot list all churches."""
        res = self.client.get(CHURCH_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_church_unauthenticated(self):
        """Test unauthenticated cannot access the details of a church."""
        church = create_church()
        url = detail_url(church.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_church_unauthenticated(self):
        """Test unauthenticated cannot update a church."""
        church = create_church()
        payload = {'name': 'Updated Church'}
        url = detail_url(church.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        church.refresh_from_db()
        self.assertNotEqual(church.name, payload['name'])

    def test_delete_church_unauthenticated(self):
        """Test unauthenticated cannot delete a church."""
        church = create_church()
        url = detail_url(church.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateChurchAPITest(TestCase):
    """
    Test cases for authenticated users trying to access church endpoints.
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
        self.denomination = Denomination.objects.create(name="Self denom")
        self.church_data = {
            'name': 'Test Church',
            'denomination': self.denomination.id,
            'municipality': {'name': 'Test Municipality', 'province': 'UNK'}
        }

    def test_create_church_authenticated(self):
        """
        Test that authenticated users can create a new church.
        """
        denom = Denomination.objects.create(name='Other Denomination')
        payload = self.church_data
        payload.update({"denomination": denom.id})
        res = self.client.post(CHURCH_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_churches_authenticated(self):
        """
        Test that authenticated users can list all churches.
        """
        res = self.client.get(CHURCH_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_church_authenticated(self):
        """
        Test that authenticated users can access the details of a church.
        """
        church = create_church()
        url = detail_url(church.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_church_authenticated(self):
        """
        Test that authenticated users can update a church.
        """
        church = create_church()
        url = detail_url(church.id)
        denomination = Denomination.objects.create(name="Denomination Update")
        payload = {
            'name': 'New Name for Test Church',
            'denomination': denomination.id,
        }
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_church_authenticated(self):
        """
        Test that authenticated users can delete a church.
        """
        church = create_church()
        url = detail_url(church.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_denomination_returned_as_object(self):
        """Test denomination of church returned as dict."""
        church = create_church()

        denomination = serializers.DenominationSerializer(
            church.denomination
        ).data
        url = detail_url(church.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['denomination'], denomination)

    def test_create_church_with_new_priest_data(self):
        """Test creating a new Church with unexisting priest info."""
        payload = {
            "name": "New Church Name",
            "denomination": self.denomination.id,
            "priest": {
                "name": "Test Priest",
            }
        }

        res = self.client.post(CHURCH_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["priest"]['name'], payload['priest']['name'])

    def test_create_church_with_new_facilitator_data(self):
        """Test creating a new Church with unexisting facilitator info."""
        payload = {
            "name": "New Church Name",
            "denomination": self.denomination.id,
            "facilitator": {
                "name": "Test Facilitator",
            }
        }

        res = self.client.post(CHURCH_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["facilitator"]['name'],
                         payload['facilitator']['name']
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
        self.church1 = create_church(
            name="AChurch",
            denomination_name="ADenomination",
            municipality_name="AMunicipality",
            province="ART"
        )
        self.church2 = create_church(
            name="ZChurch",
            denomination_name="ZDenomination",
            municipality_name="ZMunicipality",
            province="UNK"
        )

    def test_ordering_filter(self):
        """Test ordering filter works correctly."""
        res = self.client.get(f"{CHURCH_URL}?ordering=name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church1.id)
        self.assertEqual(res.data[-1]['id'], self.church2.id)

        res = self.client.get(f"{CHURCH_URL}?ordering=-name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[-1]['id'], self.church1.id)
        self.assertEqual(res.data[0]['id'], self.church2.id)

    def test_search_filter(self):
        """Test search filter works as expected."""
        res = self.client.get(f"{CHURCH_URL}?adeno")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church1.id)

        res = self.client.get(f"{CHURCH_URL}?search=z")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church2.id)

    def test_fields_filter(self):
        """Test filter by fields works as expected."""
        res = self.client.get(f"{CHURCH_URL}?name=AChurch")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church1.id)

        res = self.client.get(
            f"{CHURCH_URL}?denomination__name=ZDenomination"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church2.id)

        res = self.client.get(
            f"{CHURCH_URL}?municipality__name=AMunicipality"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church1.id)

        res = self.client.get(
            f"{CHURCH_URL}?municipality__province=UNK"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.church2.id)

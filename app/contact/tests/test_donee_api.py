"""
Tests for the donee API.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Donee,
    Contact,
    Church,
    Municipality,
    Note,
    Denomination
)


DONEE_URL = reverse('contact:donee-list')


def detail_url(donee_id):
    """Create and return a donee's detail URL."""
    return reverse('contact:donee-detail', args=[donee_id])


def create_donee(contact_name="John", church_name="Church Name"):
    """Create and return a new donee instance."""
    contact = Contact.objects.create(name=contact_name)
    denomination = Denomination.objects.create(name="Test Denomination")
    church = Church.objects.create(name=church_name,
                                   denomination=denomination)
    donee = Donee.objects.create(
        contact=contact,
        ci="12345678901",
        church=church,
    )
    return donee


class PublicDoneeAPITests(TestCase):
    """Tests for unauthenticated users trying to access donee endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.donee_data = {
            'contact': {'name': 'John Doe'},
            'ci': '12345678901',
            'church': {'name': 'Church Name'}
        }

    def test_create_donee_unauthenticated(self):
        """Test unauthenticated cannot create a new donee."""
        res = self.client.post(DONEE_URL,
                               self.donee_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_donees_unauthenticated(self):
        """Test unauthenticated cannot list all donees."""
        res = self.client.get(DONEE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_donee_unauthenticated(self):
        """Test unauthenticated cannot access the details of a donee."""
        donee = create_donee()

        url = detail_url(donee.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_donee_unauthenticated(self):
        """Test unauthenticated cannot update a donee."""
        donee = create_donee()

        payload = {
            'contact': {'name': 'Johana'},
            'ci': '12345678902'
        }
        url = detail_url(donee.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        donee.refresh_from_db()
        self.assertNotEqual(donee.ci, payload['ci'])

    def test_delete_donee_unauthenticated(self):
        """Test unauthenticated cannot delete a donee."""
        donee = create_donee()

        url = detail_url(donee.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDoneeAPITest(TestCase):
    """
    Test cases for authenticated users trying to access donee endpoints.
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
        self.contact = Contact.objects.create(name="John")
        denomination = Denomination.objects.create(name="Church Denomination")
        self.church = Church.objects.create(
            name="Church",
            denomination=denomination,
            municipality=Municipality.objects.create(
                name="Municipality Name",
                province="PRI"),
        )
        self.donee_data = {
            'contact': {'name': 'Jane Doe'},
            'ci': '12345678902',
            'church': self.church.id
        }

    def test_create_donee_authenticated(self):
        """
        Test that authenticated users can create a new donee.
        """
        res = self.client.post(DONEE_URL,
                               self.donee_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_donees_authenticated(self):
        """
        Test that authenticated users can list all donees.
        """
        res = self.client.get(DONEE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_donee_authenticated(self):
        """
        Test that authenticated users can access the details of a donee.
        """
        donee = create_donee()

        url = detail_url(donee.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_donee_authenticated(self):
        """
        Test that authenticated users can update a donee.
        """
        donee = create_donee()

        url = detail_url(donee.id)
        res = self.client.patch(url, **self.donee_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_donee_authenticated(self):
        """
        Test that authenticated users can delete a donee.
        """
        donee = create_donee()

        url = detail_url(donee.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_donee_lists_includes_province(self):
        """Tests province attr is included on donees when listing."""
        Donee.objects.create(
            contact=self.contact,
            church=self.church
        )

        res = self.client.get(DONEE_URL)
        print(res.data)

        first_donee = res.data[0]

        self.assertIn('province', first_donee)


class DoneeModelTest(TestCase):
    """General test Cases"""
    def setUp(self):
        """Set up non-modified objects used by all test methods."""
        self.contact = Contact.objects.create(
            name="John",
            lastname="Doe",
            gender="M",
            address="123 Main St",
        )
        self.church = Church.objects.create(
            name="Church Name",
            denomination=Denomination.objects.create(name="Denomination Name"),
            priest=self.contact,
            facilitator=self.contact,
            note=Note.objects.create(note="Note content"),
            municipality=Municipality.objects.create(
                name="Municipality Name",
                province="PRI"),
            inscript=timezone.now(),
        )

    def test_donee_code_generation(self):
        """Test that the donee code is generated correctly."""
        donee = Donee.objects.create(
            contact=self.contact,
            ci="12345678901",
            church=self.church,
        )
        self.assertEqual(donee.code, f'{self.church.id}-1')
# Create another donee to test the code generation
        contact = Contact.objects.create(name="Contact")
        donee2 = Donee.objects.create(
            contact=contact,
            ci="12345678902",
            church=self.church,
        )
        self.assertEqual(donee2.code, f'{self.church.id}-2')

    def test_donee_relations(self):
        """Test the relationships between Donee and other models."""
        donee = Donee.objects.create(
            contact=self.contact,
            ci="12345678901",
            church=self.church,
        )
        self.assertEqual(donee.contact, self.contact)
        self.assertEqual(donee.church, self.church)

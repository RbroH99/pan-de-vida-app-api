"""
Tests for the phone numbers endpoints.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Contact,
    PhoneNumber
)


PHONE_NUMBER_URL = reverse('contact:phonenumber-list')


def detail_url(phone_number_id):
    """Create and return a phone_numbers's detail URL."""
    return reverse('contact:phonenumber-detail', args=[phone_number_id])


def create_user(id=99999, email="user@example.com", role=5):
    """Creates and return a new user."""
    user = get_user_model().objects.create_user(
        id=id,
        email=email,
        password="testpass123",
        role=role
    )

    return user


def create_contact(name="Phone Contact"):
    """Create and return a new contact."""
    contact = Contact.objects.create(name="Phone Contact")

    return contact


class PublicPhoneNumberAPITests(TestCase):
    """Test public request to the phone number API."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_create_phone_number(self):
        """Test creating a new phone number instance in DB."""
        contact = create_contact()
        payload = {
            "contact": contact.id,
            "number": "+53599999999"
        }
        res = self.client.post(PHONE_NUMBER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("phonenumber", res.data)

    def test_anonymous_list_phone_numbers(self):
        """Test unauthenticated trying to list phone numbers."""
        contact = create_contact()
        PhoneNumber.objects.create(contact=contact, number="+53591111111")
        PhoneNumber.objects.create(contact=contact, number="+53592222222")

        res = self.client.get(PHONE_NUMBER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(len(res.data), PhoneNumber.objects.count())

    def test_anonymous_update_phone_numbers(self):
        """Test unauthenticated trying to update phone number instance."""
        contact = create_contact()
        phone_number = PhoneNumber.objects.create(contact=contact,
                                                  number="+53 111111111")

        payload = {"number": "+53 22222222"}
        url = detail_url(phone_number.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        phone_number.refresh_from_db()
        self.assertNotEqual(phone_number.number, payload["number"])

    def test_anonymous_delete_phone_number(self):
        """Test unauthenticated deleting phone number results in error."""
        contact = create_contact()
        phone_number = PhoneNumber.objects.create(contact=contact,
                                                  number="+1 23456789012")

        url = detail_url(phone_number.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(PhoneNumber.objects.count(), 1)


class PrivatePhoneNumberAPITests(TestCase):
    """Test private request to the phone number API."""

    def setUp(self):
        self.user = create_user(role=1)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_authenticated_create_phone_number(self):
        """Test creating a new phone number instance in DB."""
        contact = create_contact()
        payload = {
            "contact": contact.id,
            "number": "+5399999999"
        }
        res = self.client.post(PHONE_NUMBER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("number", res.data)

    def test_create_valid_phone_number(self):
        """Test creating a valid phone number."""
        contact = create_contact()
        payload = {
            "contact": contact.id,
            "number": "+5399999999"
        }
        res = self.client.post(PHONE_NUMBER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("number", res.data)
        self.assertEqual(PhoneNumber.objects.count(), 1)
        self.assertEqual(PhoneNumber.objects.get().number, payload["number"])

    def test_create_invalid_phone_number(self):
        """Test creating an invalid phone number."""
        contact = create_contact()
        payload = {
            "contact": contact.id,
            "number": "+123 456 789 1011 12"
        }
        res = self.client.post(PHONE_NUMBER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("phonenumber", res.data)
        self.assertEqual(PhoneNumber.objects.count(), 0)

    def test_list_phone_numbers(self):
        """Test listing phone numbers."""
        contact = create_contact()
        PhoneNumber.objects.create(contact=contact, number="+53591111111")
        PhoneNumber.objects.create(contact=contact, number="+53592222222")

        res = self.client.get(PHONE_NUMBER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_update_phone_number(self):
        """Test updating a phone number."""
        contact = create_contact()
        phone_number = PhoneNumber.objects.create(contact=contact,
                                                  number="+53591111111")
        payload = {"number": "+53592222222"}
        url = detail_url(phone_number.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        phone_number.refresh_from_db()
        self.assertEqual(phone_number.number, payload["number"])

    def test_delete_phone_number(self):
        """Test deleting a phone number."""
        contact = create_contact()
        phone_number = PhoneNumber.objects.create(contact=contact,
                                                  number="+53591111111")
        url = detail_url(phone_number.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PhoneNumber.objects.count(), 0)

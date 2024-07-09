"""
Tests for the Contact API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Contact
from core.utils import gender_choices


CONTACTS_URL = reverse('contact:contact-list')


GENDER_CHOICES_URL = reverse('contact:gender-choices')


def detail_url(contact_id):
    """Create and return a contact's detail URL."""
    return reverse('contact:contact-detail', args=[contact_id])


def create_user(id=99999, email="user@example.com"):
    """Creates and return a new user."""
    user = get_user_model().objects.create_user(id=id, email=email)

    return user


class PublicContactAPITests(TestCase):
    """Test public request to the contact API."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_create_contact(self):
        """Test unauthenticated creating a contact results in error."""
        user = create_user()
        payload = {
            "name": "Name",
            "lastname": "Last Name",
            "gender": "M",
            "user": user.id,
            "address": "St.Domingo 114A b/Heroes Lane and Columbia, Tijuana."
        }
        res = self.client.post(CONTACTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_list_contacts(self):
        """Test unauthenticated trying to list contacts in the DB."""
        res = self.client.get(CONTACTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_update_contact(self):
        """Test unauthenticathed update contact instance in the DB."""
        contact = Contact.objects.create(name="Testname")

        url = detail_url(contact.id)
        payload = {"name": "Newname"}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        contact.refresh_from_db()
        self.assertNotEqual(contact.name, payload["name"])

    def test_anonymous_delete_contact(self):
        """Tests unauthenticated delete contact instance."""
        contact = Contact.objects.create(name="Testname")

        url = detail_url(contact.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        contact.refresh_from_db()
        self.assertIsInstance(contact, Contact)


class PrivateContactAPITests(TestCase):
    """Tests for the authenticated requests to contact API."""

    def setUp(self):
        self.user = create_user(11111, 'user1@example.com')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_contact(self):
        """Test authenticated creating a contact success."""
        user = create_user()
        payload = {
            "name": "Name",
            "lastname": "Last Name",
            "gender": "M",
            "user": user.id,
            "address": "St.Domingo 114A b/Heroes Lane and Columbia, Tijuana."
        }
        res = self.client.post(CONTACTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_contacts(self):
        """Test authenticated list contacts in the DB."""
        res = self.client.get(CONTACTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_contact(self):
        """Test authenticathed update contact instance in the DB."""
        contact = Contact.objects.create(name="Testname")

        url = detail_url(contact.id)
        payload = {"name": "Newname"}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.name, payload["name"])

    def test_delete_contact(self):
        """Tests authenticated delete contact instance."""
        contact = Contact.objects.create(name="Testname")

        url = detail_url(contact.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(contact, Contact.objects.all())

    def test_gender_choices_api_view(self):
        """Test contact gender choices retrieve endpoint."""

        res = self.client.get(GENDER_CHOICES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expected_data = [
            {'label': choice[1], 'value': choice[0]}
            for choice in gender_choices
        ]
        self.assertListEqual(res.data, expected_data)

    def test_create_note_on_contact_create(self):
        """"Test creating a new note on a new contact creation."""
        user = create_user()
        payload = {
            "name": "Name",
            "lastname": "Last Name",
            "gender": "M",
            "user": user.id,
            "address": "St.Domingo 114A b/Heroes Lane and Columbia, Tijuana.",
            "note": {"note": "Nota de prueba para la api."},
        }
        res = self.client.post(CONTACTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

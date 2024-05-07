"""
Tests for the patient API.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Patient,
    Contact,
    Church,
    Municipality,
    Note,
    Denomination
)


PATIENT_URL = reverse('contact:patient-list')


def detail_url(patient_id):
    """Create and return a patient's detail URL."""
    return reverse('contact:patient-detail', args=[patient_id])


def create_patient(contact_name="John", church_name="Church Name"):
    """Create and return a new patient instance."""
    contact = Contact.objects.create(name=contact_name)
    denomination = Denomination.objects.create(name="Test Denomination")
    church = Church.objects.create(name=church_name,
                                   denomination=denomination)
    patient = Patient.objects.create(
        contact=contact,
        ci="12345678901",
        church=church,
    )
    return patient


class PublicPatientAPITests(TestCase):
    """Tests for unauthenticated users trying to access patient endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.patient_data = {
            'contact': {'name': 'John Doe'},
            'ci': '12345678901',
            'church': {'name': 'Church Name'}
        }

    def test_create_patient_unauthenticated(self):
        """Test unauthenticated cannot create a new patient."""
        res = self.client.post(PATIENT_URL,
                               self.patient_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_patients_unauthenticated(self):
        """Test unauthenticated cannot list all patients."""
        res = self.client.get(PATIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_patient_unauthenticated(self):
        """Test unauthenticated cannot access the details of a patient."""
        patient = create_patient()

        url = detail_url(patient.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_patient_unauthenticated(self):
        """Test unauthenticated cannot update a patient."""
        patient = create_patient()

        payload = {
            'contact': {'name': 'Johana'},
            'ci': '12345678902'
        }
        url = detail_url(patient.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        patient.refresh_from_db()
        self.assertNotEqual(patient.ci, payload['ci'])

    def test_delete_patient_unauthenticated(self):
        """Test unauthenticated cannot delete a patient."""
        patient = create_patient()

        url = detail_url(patient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePatientAPITest(TestCase):
    """
    Test cases for authenticated users trying to access patient endpoints.
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
        denomination = Denomination.objects.create(name="Church Denomination")
        church = Church.objects.create(name="Churc", denomination=denomination)
        self.patient_data = {
            'contact': {'name': 'Jane Doe'},
            'ci': '12345678902',
            'church': church.id
        }

    def test_create_patient_authenticated(self):
        """
        Test that authenticated users can create a new patient.
        """
        res = self.client.post(PATIENT_URL,
                               self.patient_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_patients_authenticated(self):
        """
        Test that authenticated users can list all patients.
        """
        res = self.client.get(PATIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_patient_authenticated(self):
        """
        Test that authenticated users can access the details of a patient.
        """
        patient = create_patient()

        url = detail_url(patient.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_patient_authenticated(self):
        """
        Test that authenticated users can update a patient.
        """
        patient = create_patient()

        url = detail_url(patient.id)
        res = self.client.patch(url, **self.patient_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_patient_authenticated(self):
        """
        Test that authenticated users can delete a patient.
        """
        patient = create_patient()

        url = detail_url(patient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class PatientModelTest(TestCase):
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
                province="UNK"),
            inscript=timezone.now(),
        )

    def test_patient_code_generation(self):
        """Test that the patient code is generated correctly."""
        patient = Patient.objects.create(
            contact=self.contact,
            ci="12345678901",
            church=self.church,
        )
        self.assertEqual(patient.code, f'{self.church.id}-1')
# Create another patient to test the code generation
        contact = Contact.objects.create(name="Contact")
        patient2 = Patient.objects.create(
            contact=contact,
            ci="12345678902",
            church=self.church,
        )
        self.assertEqual(patient2.code, f'{self.church.id}-2')

    def test_patient_relations(self):
        """Test the relationships between Patient and other models."""
        patient = Patient.objects.create(
            contact=self.contact,
            ci="12345678901",
            church=self.church,
        )
        self.assertEqual(patient.contact, self.contact)
        self.assertEqual(patient.church, self.church)

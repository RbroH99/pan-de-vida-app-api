"""
Tests for the disease API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Medicine,
    Disease,
    Treatment,
    Contact,
    Donee,
    Church
)


DISEASE_URL = reverse('medicine:disease-list')


def detail_url(disease_id):
    """Create and return a disease's detail URL."""
    return reverse('medicine:disease-detail', args=[disease_id])


def create_disease(name="Test Disease"):
    """Create and return a new disease instance."""
    disease = Disease.objects.create(name=name)
    return disease


def create_medicine(name="Test Medication"):
    """Create and return new medicine instance."""
    medicine = Medicine.objects.create(name=name)
    return medicine


def create_donee(
        contact_name="Donee Contact",
        church_name="Donee Church",
        donee_ci="12345678909"
):
    """Creates a donee instance and returns it."""
    try:
        donee_contact = Contact.objects.create(name=contact_name)
        donee_church = Church.objects.create(name=church_name)
        donee = Donee.objects.create(
            contact=donee_contact,
            church=donee_church,
            ci=donee_ci
        )

        return donee
    except Exception as e:
        print("Exception :" + e)


def create_treatment(medicine, disease, donee):
    """
    Create and return new treatments
    instance associated to disease.
    """
    treatment = Treatment.objects.create(
        donee=donee,
        disease=disease
    )
    treatment.medicine.add(medicine.id)

    return treatment


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

    def test_get_disease_with_treatments(self):
        """Verify endpoint return correct associated medicines."""
        medicine1 = create_medicine("Medication 1")
        medicine2 = create_medicine("Medication 2")

        disease = create_disease(name="Test Disease for Treatments")

        donee = create_donee()

        create_treatment(medicine1, disease, donee)
        create_treatment(medicine2, disease, donee)

        res = self.client.get(DISEASE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("treatments", res.data[-1])
        self.assertEqual(len(res.data[-1]["treatments"]), 2)

    def test_retrieve_diseases_patients(self):
        """Verify custom action 'patients' returns the correct donees."""
        donee = create_donee()
        medicine = create_medicine()
        disease = create_disease()
        create_treatment(medicine, disease, donee)

        url = detail_url(disease.id)
        res = self.client.get(f"{url}patients/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['ci'], donee.ci)

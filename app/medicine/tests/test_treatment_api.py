"""
Tests for the Treatment API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Treatment,
    Disease,
    Medicine,
    Donee,
    Denomination,
    Contact,
    Church
)


TREATMENT_URL = reverse('medicine:treatment-list')


def detail_url(treatment_id):
    """Create and return a treatment's detail URL."""
    return reverse('medicine:treatment-detail', args=[treatment_id])


class PublicTreatmentAPITest(TestCase):
    """Tests for unauthenticated users trying to access treatment endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.donee = Donee.objects.create(
            contact=Contact.objects.create(name="John Doe"),
            ci="12345678901",
            church=Church.objects.create(
                name="Church Name",
                denomination=Denomination.objects.create(
                    name="Denomination Name"
                )
            )
        )
        self.disease = Disease.objects.create(name="Disease Name")
        self.medicine = Medicine.objects.create(name="Medicine Name")
        self.treatment_data = {
            'donee': self.donee.id,
            'disease': self.disease.id,
            'medicine': [self.medicine.id]
        }

    def test_create_treatment_unauthenticated(self):
        """Test unauthenticated cannot create a new treatment."""
        res = self.client.post(TREATMENT_URL,
                               self.treatment_data,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_treatments_unauthenticated(self):
        """Test unauthenticated cannot list all treatments."""
        res = self.client.get(TREATMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_treatment_unauthenticated(self):
        """Test unauthenticated cannot access the details of a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_treatment_unauthenticated(self):
        """Test unauthenticated cannot update a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        new_medicine = Medicine.objects.create(name="New Medicine")
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.patch(url,
                                {'medicine': [new_medicine.id]},
                                format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_treatment_unauthenticated(self):
        """Test unauthenticated cannot delete a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTreatmentAPITest(TestCase):
    """Tests for authenticated users trying to access treatment endpoints."""

    def setUp(self):
        """Set up the test environment for authenticated users."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            id=999999,
            email='test@example.com',
            password='testpass',
            role=1,
        )
        self.client.force_authenticate(user=self.user)
        self.donee = Donee.objects.create(
            contact=Contact.objects.create(name="Jane Doe"),
            ci="12345678902",
            church=Church.objects.create(
                name="Church Name",
                denomination=Denomination.objects.create(
                    name="Denomination Name")
                )
        )
        self.disease = Disease.objects.create(name="Disease Name")
        self.medicine = Medicine.objects.create(name="Medicine Name")
        self.treatment_data = {
            'donee': self.donee.id,
            'disease': self.disease.id,
            'medicine': [self.medicine.id]
        }

    def test_create_treatment_authenticated(self):
        """Test that authenticated users can create a new treatment."""
        res = self.client.post(TREATMENT_URL,
                               self.treatment_data,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_treatments_authenticated(self):
        """Test that authenticated users can list all treatments."""
        res = self.client.get(TREATMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_treatment_authenticated(self):
        """Test authenticated users can access the details of a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_treatment_authenticated(self):
        """Test that authenticated users can update a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        new_medicine = Medicine.objects.create(name="New Medicine")
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.patch(url,
                                {'medicine': [new_medicine.id]},
                                format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_treatment_authenticated(self):
        """Test that authenticated users can delete a treatment."""
        treatment = Treatment.objects.create(donee=self.donee,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class PrivateFilteringAPITests(TestCase):
    """Test cases for the filtering and ordering in API responses."""

    def setUp(self):
        """
        Set up the test environment for authenticated users.
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            id=999998,
            email='test@example.com',
            password='testpass',
            role=1
        )
        self.client.force_authenticate(user=self.user)
        self.disease1 = Disease.objects.create(name="Alzheimer")
        self.disease2 = Disease.objects.create(name="Zenophobia")
        self.contact1 = Contact.objects.create(name='Anna', lastname='Abbott')
        self.contact2 = Contact.objects.create(name='Zoe', lastname='Zelenia')
        self.church = Church.objects.create(name="Church Name")
        self.medicine1 = Medicine.objects.create(name="AMedicine")
        self.medicine2 = Medicine.objects.create(name="ZMedicine")
        self.donee1 = Donee.objects.create(
            ci="253647835463",
            contact=self.contact1,
            church=self.church
        )
        self.donee2 = Donee.objects.create(
            ci="343647835463",
            contact=self.contact2,
            church=self.church
        )
        self.treatment1 = Treatment.objects.create(
            donee=self.donee1,
            disease=self.disease1,
        )
        self.treatment2 = Treatment.objects.create(
            donee=self.donee2,
            disease=self.disease2,
        )
        self.client.patch(
            detail_url(self.treatment1.id),
            {'medicine': [self.medicine1.id]},
            format='json'
        )
        self.client.patch(
            detail_url(self.treatment2.id),
            {'medicine': [self.medicine2.id]},
            format='json'
        )

    def test_ordering_filter(self):
        """Test ordering filter works correctly."""
        res = self.client.get(f"{TREATMENT_URL}?ordering=donee__contact__name")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.treatment1.id)
        self.assertEqual(res.data[-1]['id'], self.treatment2.id)

        res = self.client.get(
            f"{TREATMENT_URL}?ordering=-donee__contact__lastname"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[-1]['id'], self.treatment1.id)
        self.assertEqual(res.data[0]['id'], self.treatment2.id)

    def test_search_filter(self):
        """Test search filter works as expected."""
        res = self.client.get(f"{TREATMENT_URL}?anna")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.treatment1.id)

        res = self.client.get(f"{TREATMENT_URL}?search=zele")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['id'], self.treatment2.id)

    def test_fields_filter(self):
        """Test filter by fields works as expected."""
        res = self.client.get(f"{TREATMENT_URL}?medicine=AMedicine")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.medicine1.id)

        res = self.client.get(f"{TREATMENT_URL}?disease=Zenophobia")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.medicine2.id)

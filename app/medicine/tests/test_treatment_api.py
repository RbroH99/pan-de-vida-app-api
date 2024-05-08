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
    Patient,
    Denomination,
    Contact,
    Church
)


TREATMENT_URL = reverse('medicine:treatment-list')


class PublicTreatmentAPITest(TestCase):
    """Tests for unauthenticated users trying to access treatment endpoints."""

    def setUp(self):
        """Set up the test environment for unauthenticated users."""
        self.client = APIClient()
        self.patient = Patient.objects.create(
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
            'patient': self.patient.id,
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
        treatment = Treatment.objects.create(patient=self.patient,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_treatment_unauthenticated(self):
        """Test unauthenticated cannot update a treatment."""
        treatment = Treatment.objects.create(patient=self.patient,
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
        treatment = Treatment.objects.create(patient=self.patient,
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
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
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
            'patient': self.patient.id,
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
        treatment = Treatment.objects.create(patient=self.patient,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_treatment_authenticated(self):
        """Test that authenticated users can update a treatment."""
        treatment = Treatment.objects.create(patient=self.patient,
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
        treatment = Treatment.objects.create(patient=self.patient,
                                             disease=self.disease)
        treatment.medicine.add(self.medicine)
        url = reverse('medicine:treatment-detail', args=[treatment.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

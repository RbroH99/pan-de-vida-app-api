"""
Tests for the medicine API with custom actions.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Medicine, MedClass, MedicinePresentation

from medicine.serializers import MedicineSerializer

from unittest.mock import Mock

from decimal import Decimal

MEDICINE_URL = reverse('medicine:medicine-list')


def detail_url(medicine_id):
    """Create and return a medicine detail URL."""
    return reverse('medicine:medicine-detail', args=[medicine_id])


def create_medicine(
    name="Test Name",
    med_class_name="Classification Name",
    presentation_name='Presentation Name',
    measurement=200,
    measurement_units="mg",
    quantity=10
):
    """Helper function to create a medicine."""
    classification = MedClass.objects.create(name=med_class_name)
    presentation = MedicinePresentation.objects.create(
        name=presentation_name
    )
    return Medicine.objects.create(
        name=name,
        classification=classification,
        presentation=presentation,
        measurement=measurement,
        measurement_units=measurement_units,
        quantity=quantity
    )


class PrivateMedicineCustomActionsAPITests(TestCase):
    """Test for the private API requests, including custom actions."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9999,
            email='testuser@example.com',
            password='testpass123',
            name='Test User',
            role=1
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_primary_group(self):
        """Test the primary_group custom action."""
        create_medicine(name="Medicine1", quantity=5)
        create_medicine(name="Medicine1", presentation_name="Box", quantity=10)
        create_medicine(name="Medicine2", quantity=15)

        url = reverse('medicine:medicine-primary-group')
        res = self.client.get(f"{url}?limit=3&offset=0")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # medicines = Medicine.objects.defer('expiration_date').order_by(
        #     'name', 'measurement_units', 'measurement', 'presentation__name'
        # ).distinct().annotate(total_quantity=Sum('quantity'))

        # Verify pagination in the results
        self.assertIn('results', res.data)

    def test_primary_group_ordering(self):
        """Test the primary_group custom action accepts ordering."""
        create_medicine(name="Medicine1", quantity=5)
        create_medicine(name="Medicine1", presentation_name="Box", quantity=10)
        create_medicine(name="Medicine2", quantity=15)

        url = reverse('medicine:medicine-primary-group')
        res = self.client.get(f"{url}?limit=3&offset=0&ordering=-name")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        medicines = Medicine.objects.defer('expiration_date').order_by("-name")

        request_mock = Mock()
        request_mock.user = self.user
        self.assertEqual(res.data['results'][0]["name"], medicines[0].name)

    def test_name_group(self):
        """Test the name_group custom action."""
        create_medicine(name="Medicine1", measurement=50, quantity=5)
        create_medicine(
            name="Medicine1",
            presentation_name="Box",
            measurement=100,
            quantity=10)
        create_medicine(name="Medicine2", measurement=75, quantity=15)

        url = reverse('medicine:medicine-name-group')
        res = self.client.get(
            f"{url}?name=Medicine1&presentation=Box&limit=2&offset=0"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        medicines = Medicine.objects.filter(
            name="Medicine1",
            presentation__name="Box"
        ).order_by(
            'name',
            'expiration_date',
            'measurement_units',
            'measurement',
            'presentation'
        )

        self.assertIn('results', res.data)
        request_mock = Mock()
        request_mock.user = self.user
        serializer = MedicineSerializer(
            medicines, many=True, context={'request': request_mock}
        )
        self.assertEqual(res.data['results'], serializer.data)

    def test_show_zero_param(self):
        """Test the show_zero query param works correctly."""
        create_medicine(name="Medicine1", measurement=50, quantity=5)
        create_medicine(
            name="Medicine1",
            presentation_name="Box",
            measurement=100,
            quantity=10)
        create_medicine(name="Medicine2", measurement=75, quantity=0)

        url = reverse('medicine:medicine-name-group')
        res = self.client.get(
            f"{url}?name=Medicine2&presentation=Box&limit=2&offset=0&"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn('results', res.data)
        self.assertEqual(res.data['results'], [])

    def test_grouped_medicines(self):
        """Test the grouped_medicines custom action."""
        create_medicine(
            name="Medicine1",
            measurement=50,
            measurement_units="mg",
            quantity=5)
        create_medicine(
            name="Medicine1",
            measurement=100,
            measurement_units="mg",
            quantity=10)
        create_medicine(
            name="Medicine2",
            measurement=200,
            measurement_units="ml",
            quantity=15)

        url = reverse('medicine:medicine-grouped-medicines')
        res = self.client.get(f"{url}?limit=3&offset=0")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = {
            "Medicine1": [
                {"id": 1, "measurement": 50, "measurement_units": "mg"},
                {"id": 2, "measurement": 100, "measurement_units": "mg"}
            ],
            "Medicine2": [
                {"id": 3, "measurement": 200, "measurement_units": "ml"}
            ]
        }

        self.assertEqual(res.data, expected_data)

    def test_grouped_medicines_with_filter(self):
        """Test the grouped_medicines action with a filter by name."""
        create_medicine(
            name="Medicine1", measurement=50, measurement_units="mg", quantity=5
            )
        create_medicine(
            name="Medicine1",
            measurement=100,
            measurement_units="mg",
            quantity=10)
        create_medicine(
            name="Medicine2",
            measurement=200,
            measurement_units="ml",
            quantity=15
        )

        url = reverse('medicine:medicine-grouped-medicines')
        res = self.client.get(f"{url}?name=Medicine1")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = {
            "Medicine1": [
                {"id": 1, "measurement": 50, "measurement_units": "mg"},
                {"id": 2, "measurement": 100, "measurement_units": "mg"}
            ]
        }

        self.assertEqual(res.data, expected_data)

    def test_grouped_medicines_with_show_zero(self):
        """Test the grouped_medicines action with show_zero parameter."""
        create_medicine(
            name="Medicine1",
            measurement=50,
            measurement_units="mg",
            quantity=0)
        create_medicine(
            name="Medicine1",
            measurement=100,
            measurement_units="mg",
            quantity=10)
        create_medicine(
            name="Medicine2",
            measurement=200,
            measurement_units="ml",
            quantity=0)

        url = reverse('medicine:medicine-grouped-medicines')
        res = self.client.get(f"{url}?show_zero=false&")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = {
            'Medicine1': [
                {
                    'id': 1,
                    'measurement': Decimal('50.00'),
                    'measurement_units': 'mg'},
                {
                    'id': 2,
                    'measurement': Decimal('100.00'),
                    'measurement_units': 'mg'}],
            'Medicine2': [
                {
                    'id': 3,
                    'measurement': Decimal('200.00'),
                    'measurement_units': 'ml'}]
        }

        self.assertEqual(res.data, expected_data)

    def test_grouped_medicines_empty_response(self):
        """Test the grouped_medicines action with no matching data."""
        create_medicine(
            name="Medicine1", measurement=50, measurement_units="mg", quantity=5
            )
        create_medicine(
            name="Medicine2",
            measurement=100,
            measurement_units="ml",
            quantity=10
        )

        url = reverse('medicine:medicine-grouped-medicines')
        res = self.client.get(f"{url}?name=NonExistentMedicine")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {})

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

import datetime

from rest_framework.test import APITestCase

from dispatch.serializers import DispatchSerializer

from core.models import (
    Dispatch,
    DispatchItems,
    Church,
    Medicine,
    Item,
    Donee,
    Contact
)


DISPATCH_URL = reverse("dispatch:dispatch-list")


def detail_url(dispatch_id):
    """Create and return a dispatch detail URL."""
    return reverse("dispatch:dispatch-detail", args=[dispatch_id])


class DispatchModelTests(TestCase):
    """Test models for the dispatch app."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            name='Test Dispatcher'
        )

        self.church = Church.objects.create(name='Test Church')
        self.dispatch = Dispatch.objects.create(
            church=self.church,
            dispatcher=self.user,
            date=now(),
        )

        self.donee_contact = Contact.objects.create(
            name='John Doe',
            lastname='Doe',
            gender='M',
        )

        self.donee = Donee.objects.create(
            ci='241336523453',
            church=self.church,
            contact=self.donee_contact
        )

        self.item_medicine = Medicine.objects.create(name='Test Medicine')
        self.item_article = Item.objects.create(name='Test Article')

        self.dispatch_stock_item = DispatchItems.objects.create(
            dispatch=self.dispatch,
            quantity=10,
            beneficiary=None,
            stock=True,
            item=self.item_medicine
        )

        self.dispatch_item = DispatchItems.objects.create(
            dispatch=self.dispatch,
            quantity=10,
            beneficiary=self.donee,
            stock=False,
            item=self.item_medicine
        )

    def test_dispatch_model(self):
        self.assertEqual(
            str(self.dispatch),
            f'Dispatch {self.dispatch.code} - Church: {self.church}'
        )
        self.assertEqual(self.dispatch.dispatcher.name, 'Test Dispatcher')
        self.assertIsInstance(self.dispatch.date, datetime.date)

    def test_dispatch_items_model(self):
        self.assertEqual(
            str(self.dispatch_item),
            f'{self.dispatch_item.item} - Quantity: 10'
        )

    def test_dispatch_items_content_type(self):
        # Test medicine content type
        self.assertEqual(
            DispatchItems.objects.filter(
                content_type__model='medicine'
            ).count(), 2
        )

        # Test article content type (should raise ValidationError)
        with self.assertRaises(ValidationError):
            DispatchItems.objects.create(
                dispatch=self.dispatch,
                quantity=10,
                beneficiary=None,
                stock=False,
                item=self.item_article
            )

    def test_dispatch_items_item_relationship(self):
        # Test medicine item relationship
        self.assertIsInstance(self.dispatch_item.item, Medicine)

        # Test article item relationship (should raise ValidationError)
        with self.assertRaises(ValidationError):
            DispatchItems.objects.create(
                dispatch=self.dispatch,
                quantity=10,
                beneficiary=None,
                stock=False,
                item=self.item_article
            )

    def test_dispatch_items_quantity(self):
        self.assertEqual(self.dispatch_item.quantity, 10)

    def test_dispatch_items_beneficiary(self):
        self.assertIsNone(self.dispatch_stock_item.beneficiary)

    def test_dispatch_items_stock(self):
        self.assertFalse(self.dispatch_item.stock)


class DispatchSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="dispatcher@example.com",
            password="testpassword",
            name="Dispatcher Name"
        )
        self.church = Church.objects.create(name="Central Church")

        self.dispatch_data = {
            "church": self.church.id,
            "dispatcher": self.user.id,
            "receiver": "John Doe",
        }

    def test_dispatch_serializer_valid_data(self):
        """Test DispatchSerializer with valid data."""
        serializer = DispatchSerializer(data=self.dispatch_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["church"], self.church)
        self.assertEqual(serializer.validated_data["receiver"], "John Doe")

    def test_dispatch_serializer_representation(self):
        """Test the serialized representation of a Dispatch instance."""
        dispatch = Dispatch.objects.create(
            church=self.church,
            dispatcher=self.user,
            date=now(),
            receiver="John Doe"
        )
        serializer = DispatchSerializer(dispatch)
        representation = serializer.data
        self.assertEqual(representation["church"]["name"], "Central Church")
        self.assertEqual(representation["dispatcher"]["name"], self.user.name)


class DispatchAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="dispatcher@example.com",
            password="testpassword",
            role=1,
            name="dispatcher"
        )
        self.church = Church.objects.create(name="Central Church")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_dispatch(self):
        """Test creating a dispatch via API."""
        payload = {
            "church": self.church.id,
            "receiver": "John Doe",
        }
        response = self.client.post(DISPATCH_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["church"]["name"], "Central Church")
        self.assertEqual(response.data["dispatcher"]["name"], "dispatcher")

    def test_list_dispatches(self):
        """Test retrieving a list of dispatches via API."""
        Dispatch.objects.create(
            church=self.church,
            dispatcher=self.user,
            receiver="John Doe"
        )

        response = self.client.get(DISPATCH_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["church"]["name"], "Central Church")

    def test_dispatch_detail(self):
        """Test retrieving a specific dispatch by ID via API."""
        dispatch = Dispatch.objects.create(
            church=self.church,
            dispatcher=self.user,
            receiver="John Doe"
        )
        url = detail_url(dispatch.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["church"]["name"], "Central Church")
        self.assertEqual(response.data["dispatcher"]["name"], "dispatcher")

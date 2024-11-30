from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.contenttypes.models import ContentType

from core.models import (
    Dispatch,
    Church,
    Medicine,
    Item,
    Donee,
    Contact,
)


DISPATCH_URL = reverse("dispatch:dispatch-item-list")


def detail_url(dispatch_item_id):
    """Create and return a dispatch item detail URL."""
    return reverse("dispatch:dispatch-item-detail", args=[dispatch_item_id])


class DispatchItemAPITests(TestCase):
    """Test models for the dispatch app."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            name='Test Dispatcher',
            role=1
        )
        self.agent_client = APIClient()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

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
            contact=self.donee_contact,
        )

        self.medicine = Medicine.objects.create(name='Test Medicine',
                                                quantity=20)
        self.item = Item.objects.create(name='Test Item',
                                        quantity=20)

    def test_create_new_dispatch_item(self):
        """Test creating new dispatch item results in success."""
        content_type = ContentType.objects.get_for_model(Medicine).id
        payload = {
            'dispatch': self.dispatch.id,
            'beneficiary': self.donee.id,
            'quantity': 10,
            'stock': False,
            'content_type': content_type,
            'object_id': self.medicine.id,
        }

        res = self.client.post(DISPATCH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['quantity'], 10)

    def test_create_new_dispatch_item_invalid_quantity(self):
        """Test trying to create item with invalid quantity results in error."""
        content_type = ContentType.objects.get_for_model(Item).id
        payload = {
            'dispatch': self.dispatch.id,
            'beneficiary': self.donee.id,
            'quantity': -10,
            'stock': False,
            'content_type': content_type,
            'object_id': self.item.id,
        }

        res = self.client.post(DISPATCH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', res.data)

        payload["quantity"] = 50
        res = self.client.post(DISPATCH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', res.data)

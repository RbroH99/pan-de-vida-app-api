from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.models import Announcement


ANNOUNCEMENTS_URL = reverse('announcement:announcement-list')


class AnnouncementAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser',
            password='testpass',
            role=1,
        )
        self.client.force_authenticate(user=self.user)
        self.url = ANNOUNCEMENTS_URL

    def test_create_announcement(self):
        data = {
            "title": "Test Announcement",
            "content": "This is a test announcement.",
            "initial_date": "2023-10-01",
            "final_date": "2023-10-10",
            "directed_to": [1, 2],
            "is_public": False,
        }
        res = self.client.post(self.url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.count(), 1)
        # Test author is the user that created it.
        author_info = {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email
        }
        self.assertEqual(res.data["author"], author_info)

    def test_create_announcement_with_insuficient_permission(self):
        """
        Test creating a new announcement with an user that is not
        admin or colaborator.
        """
        data = {
            "title": "Test Announcement",
            "content": "This is a test announcement.",
            "initial_date": "2023-10-01",
            "final_date": "2023-10-10",
            "directed_to": [1, 2],
            "is_public": False,
        }
        user = get_user_model().objects.create_user(
            email="agentuser@example.com",
            password="testpass123",
            role=2
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_announcement_with_invalid_dates(self):
        data = {
            "title": "Test Announcement",
            "content": "This is a test announcement.",
            "initial_date": "2023-10-10",
            "final_date": "2023-10-01",
            "directed_to": [1, 2],
            "is_public": False,
            "author": self.user.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_announcement_drected_to_invalid_roles(self):
        data = {
            "title": "Test Announcement",
            "content": "This is a test announcement.",
            "initial_date": "2023-10-01",
            "final_date": "2023-10-10",
            "directed_to": [1, 99],  # 99 is an invalid role
            "is_public": False,
            "author": self.user.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_announcements(self):
        Announcement.objects.create(
            title="Test Announcement",
            content="This is a test announcement.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[1, 2],
            is_public=False,
            author=self.user
        )
        res = self.client.get(self.url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_get_announcements_with_role_filter(self):
        user = get_user_model().objects.create_user(
            email="agentuser@example.com",
            password="testpass123",
            role=2
        )
        client = APIClient()
        client.force_authenticate(user)

        Announcement.objects.create(
            title="Public Announcement",
            content="This is a public announcement.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[],
            is_public=True,
            author=self.user
        )
        Announcement.objects.create(
            title="Role Specific Announcement",
            content="This is a role specific announcement.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[2],  # Role 2 matches the user's role
            is_public=False,
            author=self.user
        )
        Announcement.objects.create(
            title="Other Role Announcement",
            content="This is an announcement for other roles.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[1, 0],
            is_public=False,
            author=self.user
        )

        response = client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 announcements
        titles = [announcement['title'] for announcement in response.data]
        self.assertIn("Public Announcement", titles)
        self.assertIn("Role Specific Announcement", titles)
        self.assertNotIn("Other Role Announcement", titles)

    def test_get_announcements_with_search_filter(self):
        Announcement.objects.create(
            title="Test Announcement Search",
            content="This is a test announcement.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[1, 2],
            is_public=False,
            author=self.user
        )
        Announcement.objects.create(
            title="Test Announcement Nothing",
            content="This is a test announcement.",
            initial_date="2023-10-01",
            final_date="2023-10-10",
            directed_to=[1, 2],
            is_public=False,
            author=self.user
        )
        res = self.client.get(f"{self.url}?search=search", format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        res = self.client.get(f"{self.url}?search=pope/", format='json')
        self.assertEqual(len(res.data), 0)

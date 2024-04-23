"""
Tests suite for the note API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Note


NOTES_URL = reverse('contact:note-list')


def detail_url(note_id):
    """Create and return a note detail URL."""
    return reverse('contact:note-detail', args=[note_id])


class PublicNoteAPITests(TestCase):
    """Tests for the anonymous Note API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_note_list_error(self):
        """Test unauthenticated note-list fails."""
        res = self.client.get(NOTES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_note_get_error(self):
        """Test unauthenticated getting note detail results in error."""
        note = Note.objects.create(note="Test note.")

        url = detail_url(note.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(note.note, res.data)

    def test_anonymous_note_post_error(self):
        """Test unauthenticated post to note endpoint results in error."""
        payload = {"note": "Test note."}
        res = self.client.post(NOTES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("note", res.data)

    def test_anonymous_note_update(self):
        """Test anonymous update request to note API fails."""
        note = Note.objects.create(note="Test note.")

        payload = {"note": "New Note"}
        url = detail_url(note.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        note.refresh_from_db()
        self.assertNotEqual(note.note, payload["note"])


class PrivateNoteAPITests(TestCase):
    """Tests for the authenticated medicine classification API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=9999,
            email="user2@example.com",
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_note_list(self):
        """Test authenticated note-list success."""
        res = self.client.get(NOTES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_note_get(self):
        """Test authenticated getting note detail success."""
        note = Note.objects.create(note="Test note.")

        url = detail_url(note.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(note.note, res.data['note'])

    def test_note_post(self):
        """Test authenticated post to note success."""
        payload = {"note": "Test Note."}
        res = self.client.post(NOTES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("note", res.data)

    def test_note_update(self):
        """Test authenticated update request to note API."""
        note = Note.objects.create(note="Test Note.")

        payload = {"note": "Updated note."}
        url = detail_url(note.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.note, payload["note"])

    def test_note_delete(self):
        """Test authenticated can delete a note."""
        existing_note = Note.objects.create(note="Test note.")

        url = detail_url(existing_note.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(existing_note, Note.objects.all())

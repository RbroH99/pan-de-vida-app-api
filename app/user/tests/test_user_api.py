"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_PAIR_URL = reverse('token_obtain_pair')
ME_URL = reverse('user:me')
ADMIN_URL = reverse('user:admin-list')


def create_user(**params):
    """Creates and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """"Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short_error(self):
        """Test an error is returned if password less than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'te',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """Test generates token for valid credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': 'pass123',
            'name': 'Test Name',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_PAIR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials not valid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': '', 'password': 'badpass'}
        res = self.client.post(TOKEN_PAIR_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting blank password returns error."""
        create_user(email='test@example.com', password='testpass123')

        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_PAIR_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTests(TestCase):
    """Test API request that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@exmple.com',
            password='testpass123',
            name='Test Name',
            role=1
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for authenticated user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
            'role': 1
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for the authenticated user."""
        payload = {'name': 'Updated Name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertTrue(res.status_code, status.HTTP_200_OK)


class RoleBasedTests(TestCase):
    """Test actions based in user role."""

    def setUp(self):
        # users declarations
        self.admin_user = create_user(
            email='testadmin@exmple.com',
            password='testpass123',
            name='Test Admin',
            role=1
        )

        self.agent_user = create_user(
            email='testagent@exmple.com',
            password='testpass123',
            name='Test Agent',
            role=2
        )

        self.donor_user = create_user(
            email='testdonor@exmple.com',
            password='testpass123',
            name='Test Donor'
        )

        # Clients definitions
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.agent_client = APIClient()
        self.agent_client.force_authenticate(user=self.agent_user)

        self.donor_client = APIClient()
        self.donor_client.force_authenticate(user=self.donor_user)

    def test_admin_retrieve_user_list(self):
        """Test admin users can retrieve users in the system."""
        res = self.admin_client.get(ADMIN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data), 1)

    def test_agent_retrieve_user_list(self):
        """Test agent users can't retrieve users in the system."""
        res = self.agent_client.get(ADMIN_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_default_role_is_donor(self):
        """Test users default role on creation is donor."""
        res = self.donor_client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["role"], 3)

    def test_donor_retrieve_user_list(self):
        """Test donor users can't retrieve users in the system."""
        res = self.donor_client.get(ADMIN_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

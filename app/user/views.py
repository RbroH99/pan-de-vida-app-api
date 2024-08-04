"""
Views for the userAPI.
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import generics, permissions, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
from django.http import Http404

from user.serializers import UserSerializer

from core.permissions import IsAdminRole


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class AdminUserViewset(viewsets.ModelViewSet):
    """Viewset for the admin users to manage users in the system."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'email']

    actions = {
        'list': ['get'],
        'create': ['post'],
        'retrieve': ['get'],
        'update': ['put', 'patch'],
        'partial_update': ['patch'],
        'destroy': ['delete']
    }

    def get_queryset(self):
        try:
            users = get_user_model().objects.exclude(id=self.request.user.id)
            return users
        except AttributeError:
            raise Http404("No se encontró el usuario.")

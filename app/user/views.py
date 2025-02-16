"""
Views for the userAPI.
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import generics, permissions, viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
from django.http import Http404

from core.utils import role_choices_spa

from user.serializers import (
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    SetPasswordSerializer,
    AdminUserSerializer
)

from core.permissions import (
    IsAdminRole,
    IsAgentMinimun,
    IsColaboratorMinimun
    )

from core.models import Contact, Church


class CreateUserView(generics.CreateAPIView):
    """View to create a new user."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AdminCreateUserView(generics.CreateAPIView):
    """View to create a new user by an admin or colaborator."""
    queryset = get_user_model().objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsColaboratorMinimun]
    http_method_names = ['post']

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class SetPasswordView(generics.GenericAPIView):
    """View to set a password for the user after confirming email."""
    serializer_class = SetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password successfully set."},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminUserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        try:
            users = get_user_model().objects.exclude(id=self.request.user.id)
            return users
        except AttributeError:
            raise Http404("User not found.")


class PasswordResetRequestView(APIView):
    """Endpoint for users to request password recuperation."""
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_password_reset_email(request)
            return Response(
                {"message": "Email with recuperation instructions sent."}
            )
        return Response(serializer.errors, status=400)


class PasswordResetView(APIView):
    """Users password reset endpoint."""
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password successfully changed."})
        return Response(serializer.errors, status=400)


class GetUserRolesView(APIView):
    """View to get the avaliables user Roles."""
    permission_classes = [permissions.IsAuthenticated, IsAgentMinimun]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        roles_choices = [
            {'label': choice[1], 'value': choice[0]}
            for choice in role_choices_spa
        ]
        return Response(roles_choices, status=status.HTTP_200_OK)


class GetAvaliablesView(APIView):
    """View to get the available contacts to associate to a user."""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        church_id = request.query_params.get("churchId", None)
        if church_id:
            try:
                church = Church.objects.get(id=church_id)
            except Church.DoesNotExist:
                return Response(
                    {"detail": f"Church with id:{church_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            contacts = Contact.objects.filter(user__isnull=True, donee__church=church)
        else:
            contacts = Contact.objects.filter(user__isnull=True)

        contact_choices = [
            {'id': contact.id, 'name': f"{contact.name} {contact.lastname}"}
            for contact in contacts
        ]
        return Response(contact_choices, status=status.HTTP_200_OK)


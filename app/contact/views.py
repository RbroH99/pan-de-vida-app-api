"""
Viewsets for the contact APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
    status,
)

from contact import serializers

from core.models import (
    Note,
    Contact,
    PhoneNumber,
    WorkingSite,
    Medic,
    Donor,
    Donee
)
from core.utils import gender_choices
from core.filters import ContactFilterset


class BasePrivateViewSet(viewsets.ModelViewSet):
    """Base authorization classes viewset for private endpoints."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']

    def _contact_children_destroy(self, request, *args, **kwargs):
        """Deletes a donee instance with his assossiated contact."""
        try:
            instance = self.get_object()
            contact = instance.contact
            note = contact.note

            if contact:
                if note:
                    note.delete()
                contact.delete()

            self.perform_destroy(instance)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error during destruction: {e}")
            return Response(
                {"detail": f"Error during destruction: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NoteViewSet(BasePrivateViewSet):
    """Viewset for the note endpoints."""
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    filter_backends = []
    filterset_fields = []
    search_fields = []
    ordering_fields = []


class ContactViewSet(BasePrivateViewSet):
    """Viewset for the Contact endpoints."""
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filterset_class = ContactFilterset
    search_fields = ['name', 'lastname']
    ordering_fields = ['name', 'lastname']
    ordering = ['name', 'lastname']


class GenderOptionsView(APIView):
    """View to get gender options. """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    # The first option always is the not set option.

    def get(self, request, format=None):
        gender_options = [
            {'label': choice[1], 'value': choice[0]}
            for choice in gender_choices
        ]
        return Response(gender_options, status=status.HTTP_200_OK)


class PhoneNumberViewSet(BasePrivateViewSet):
    """Views for the phone number API."""
    queryset = PhoneNumber.objects.all()
    serializer_class = serializers.PhoneNumberSerializer
    filterset_fields = ['contact__id', 'contact__name']
    search_fields = ['contact__name', 'contact__lastname']
    ordering_fields = []


class WorkingSiteViewSet(BasePrivateViewSet):
    """Views for the working sites."""
    queryset = WorkingSite.objects.all()
    serializer_class = serializers.WorkingSiteSerializer


class MedicViewSet(BasePrivateViewSet):
    """Views for the medic api."""
    queryset = Medic.objects.all()
    serializer_class = serializers.MedicSerializer
    filterset_fields = ['contact__gender', 'workingsite__name', 'specialty']
    search_fields = ['contact__name', 'contact__lastname']
    ordering_fields = ['contact__name', 'contact__lastname']
    ordering = ['contact__name', 'contact__lastname']

    def destroy(self, request, *args, **kwargs):
        """Deletes a medic instance with his assossiated contact."""
        return self._contact_children_destroy(request, *args, **kwargs)


class DonorViewSet(BasePrivateViewSet):
    """Views for the donor api."""
    queryset = Donor.objects.all()
    serializer_class = serializers.DonorSerializer
    filterset_fields = ['contact__gender', 'country', 'city']
    search_fields = ['contact__name', 'contact__lastname']
    ordering_fields = ['contact__name', 'contact__lastname']
    ordering = ['contact__name', 'contact__lastname']

    def destroy(self, request, *args, **kwargs):
        """Deletes a donor instance with his assossiated contact."""
        return self._contact_children_destroy(request, *args, **kwargs)


class DoneeViewSet(BasePrivateViewSet):
    """Views for the donee api."""
    queryset = Donee.objects.all()
    serializer_class = serializers.DoneeDetailSerializer
    filterset_fields = [
        'contact__gender',
        'church__denomination__name',
        'church__municipality__province']
    search_fields = ['contact__name', 'contact__lastname']
    ordering_fields = ['contact__name', 'contact__lastname']
    ordering = ['contact__name', 'contact__lastname']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.DoneeSerializer
        else:
            return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        """Deletes a donee instance with his assossiated contact."""
        return self._contact_children_destroy(request, *args, **kwargs)

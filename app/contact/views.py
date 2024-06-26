"""
Viewsets for the contact APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
)

from contact import serializers

from core.models import (
    Note,
    Contact,
    PhoneNumber,
    WorkingSite,
    Medic,
    Donor,
    Patient
)


class BasePrivateViewSet(viewsets.ModelViewSet):
    """Base authorization classes viewset for private endpoints."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class NoteViewSet(BasePrivateViewSet):
    """Viewset for the note endpoints."""
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer


class ContactViewSet(BasePrivateViewSet):
    """Viewset for the Contact endpoints."""
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer


class PhoneNumberViewSet(BasePrivateViewSet):
    """Views for the phone number API."""
    queryset = PhoneNumber.objects.all()
    serializer_class = serializers.PhoneNumberSerializer


class WorkingSiteViewSet(BasePrivateViewSet):
    """Views for the working sites."""
    queryset = WorkingSite.objects.all()
    serializer_class = serializers.WorkingSiteSerializer


class MedicViewSet(BasePrivateViewSet):
    """Views for the medic api."""
    queryset = Medic.objects.all()
    serializer_class = serializers.MedicSerializer


class DonorViewSet(BasePrivateViewSet):
    """Views for the donor api."""
    queryset = Donor.objects.all()
    serializer_class = serializers.DonorSerializer


class PatientViewSet(BasePrivateViewSet):
    """Views for the patient api."""
    queryset = Patient.objects.all()
    serializer_class = serializers.PatientSerializer

"""
Viewsets for the contact APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

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

class GenderOptionsView(APIView):
    """View to get gender options. """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    #The first option always is the not set option.

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


class DoneeViewSet(BasePrivateViewSet):
    """Views for the donee api."""
    queryset = Donee.objects.all()
    serializer_class = serializers.DoneeSerializer

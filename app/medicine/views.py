"""
Views for the medicine API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
)

from medicine import serializers

from core. models import (
    MedClass,
    MedicinePresentation
)


class BasicNameOnlyPrivateModel(viewsets.ModelViewSet):
    """Basic view Authorization for name-only models."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class MedClassViewSet(BasicNameOnlyPrivateModel):
    """Manage medicine classifications."""
    serializer_class = serializers.MedClassSerializer
    queryset = MedClass.objects.all()


class MedicinePresentationViewSet(BasicNameOnlyPrivateModel):
    serializer_class = serializers.MedicinePresentationSerializer
    queryset = MedicinePresentation.objects.all()

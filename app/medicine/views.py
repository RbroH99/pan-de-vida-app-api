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
    MedicinePresentation,
    Medicine,
    Disease,
    Treatment
)


class BaseNameOnlyPrivateModel(viewsets.ModelViewSet):
    """Basic view Authorization for name-only models."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class MedClassViewSet(BaseNameOnlyPrivateModel):
    """Manage medicine classifications."""
    serializer_class = serializers.MedClassSerializer
    queryset = MedClass.objects.all()


class MedicinePresentationViewSet(BaseNameOnlyPrivateModel):
    serializer_class = serializers.MedicinePresentationSerializer
    queryset = MedicinePresentation.objects.all()


class MedicineViewSet(BaseNameOnlyPrivateModel):
    """Manage medicine in the system."""
    serializer_class = serializers.MedicineDetailSerializer
    queryset = Medicine.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.MedicineSerializer

        return self.serializer_class


class DiseaseViewSet(BaseNameOnlyPrivateModel):
    """Manage disease endpoints."""
    serializer_class = serializers.DiseaseSerializer
    queryset = Disease.objects.all()


class TreatmentViewSet(viewsets.ModelViewSet):
    """Manage treatments."""
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatment.objects.all()

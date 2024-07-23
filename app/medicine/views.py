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
    serializer_class = serializers.MedicineSerializer
    queryset = Medicine.objects.all()

    def perform_create(self, serializer):
        if 'classification' in self.request.data:
            med_class_name = self.request.data.get(
                'classification'
            ).get('name')
            med_class, created = MedClass.objects.get_or_create(
                name=med_class_name
            )
            serializer.save(classification=med_class)
        if 'presentation' in self.request.data:
            presentation_name = self.request.data.get(
                'presentation'
            ).get('name')
            presentation, created = \
                MedicinePresentation.objects.get_or_create(
                    name=presentation_name
                )
            serializer.save(presentation=presentation)
        return serializer.save()


class DiseaseViewSet(BaseNameOnlyPrivateModel):
    """Manage disease endpoints."""
    serializer_class = serializers.DiseaseSerializer
    queryset = Disease.objects.all()

    def get_serializer_class(self):
        """Returns serializer according to the request method."""
        if self.action == 'list':
            return serializers.DiseaseListSerializer
        else:
            return self.serializer_class


class TreatmentViewSet(BaseNameOnlyPrivateModel):
    """Manage treatments."""
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatment.objects.all()

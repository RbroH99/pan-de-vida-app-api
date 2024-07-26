"""
Views for the medicine API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import (
    viewsets,
)

from medicine import serializers

from contact.serializers import DoneeSerializer

from core. models import (
    MedClass,
    MedicinePresentation,
    Medicine,
    Disease,
    Treatment,
    Donee
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

    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        """Returns all patients for a disease."""
        disease = self.get_object()
        treatments_with_disease = Treatment.objects.filter(disease=disease)
        donee_ids = treatments_with_disease.values_list('donee', flat=True)
        donees = Donee.objects.filter(id__in=list(donee_ids))
        serializer = DoneeSerializer(donees, many=True)

        return Response(serializer.data)


class TreatmentViewSet(BaseNameOnlyPrivateModel):
    """Manage treatments."""
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatment.objects.all()

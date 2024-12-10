"""
Views for the medicine API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Sum

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import (
    viewsets,
)

from medicine import serializers

from contact.serializers import DoneeSerializer

from core.filters import TreatmentFilter
from core. models import (
    MedClass,
    MedicinePresentation,
    Medicine,
    Disease,
    Treatment,
    Donee
)
from core.permissions import (
    IsNotDonor
)


class BaseNameOnlyPrivateModel(viewsets.ModelViewSet):
    """Basic view Authorization for name-only models."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNotDonor]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']


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
    filterset_fields = ['name', 'classification__name', 'presentation__name']
    search_fields = ['name']
    ordering_fields = ['name', 'presentation__name', 'measurement']
    ordering = ['name', 'presentation__name', 'measurement']

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

    @action(
            detail=False, methods=['get'], url_path='primary-group')
    def primary_group(self, request):
        """
        Returns medicines grouped by name first and after by presentation,
        ordered by the measurement and adding the total quantity.
        """
        queryset = self.filter_queryset(
            self.get_queryset()
            .defer('expiration_date')
            .values(
                'name',
                'presentation',
                'classification',
                'measurement',
                'measurement_units'
            )
            .order_by('measurement_units', 'measurement', 'presentation__name')
            .annotate(total_quantity=Sum('quantity'))
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MedicineSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        ordering = request.query_params.get("ordering", None)
        if ordering:
            queryset = self.get_queryset().order_by(ordering)

        serializer = serializers.MedicineSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
            detail=False, methods=['get'], url_path='name-group')
    def name_group(self, request):
        """
        Returns medicines for a given name and presentation,
        ordered by measurement
        """
        queryset = self.get_queryset().order_by(
                'name',
                'expiration_date',
                'measurement_units',
                'measurement',
                'presentation'
            ).filter(
                name=self.request.query_params.get('name'),
            )

        presentation_name = self.request.query_params.get('presentation', None)
        if presentation_name:
            try:
                presentation_id = MedicinePresentation.objects.get(
                    name=presentation_name
                ).id
                queryset = queryset.filter(presentation=presentation_id)
            except MedicinePresentation.DoesNotExist:
                return Response(
                    {"detail": "Presentation does not exist"},
                    status=400
                )

        measurement = self.request.query_params.get('measurement', None)
        measurement_units = self.request.query_params.get(
            'measurement_units',
            None
        )
        if measurement:
            if measurement_units:
                queryset = queryset.filter(measurement_units=measurement_units)
            queryset = queryset.filter(measurement=measurement)

        show_zero = self.request.query_params.get("show_zero", False)
        if not show_zero:
            queryset = queryset.filter(quantity__gt=0)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MedicineSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = serializers.MedicineSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class DiseaseViewSet(BaseNameOnlyPrivateModel):
    """Manage disease endpoints."""
    serializer_class = serializers.DiseaseSerializer
    queryset = Disease.objects.all()
    filterset_fields = []

    def get_serializer_class(self):
        """Returns serializer according to the request method."""
        if self.action == 'list':
            return serializers.DiseaseListSerializer
        else:
            return self.serializer_class

    @action(
            detail=True, methods=['get'],
            pagination_class=LimitOffsetPagination
    )
    def patients(self, request, pk=None):
        """Returns all patients for a disease."""
        disease = self.get_object()
        treatments_with_disease = Treatment.objects.filter(disease=disease)
        donee_ids = treatments_with_disease.values_list('donee', flat=True)
        donees = Donee.objects.filter(id__in=list(donee_ids))

        page = self.paginate_queryset(donees)
        if page is not None:
            serializer = DoneeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DoneeSerializer(donees, many=True)
        return Response(serializer.data)


class TreatmentViewSet(BaseNameOnlyPrivateModel):
    """Manage treatments."""
    serializer_class = serializers.TreatmentSerializer
    queryset = Treatment.objects.all()
    filterset_class = TreatmentFilter
    search_fields = ['donee__contact__name', 'donee__contact__lastname']
    ordering_fields = ['donee__contact__name', 'donee__contact__lastname']
    ordering = ['donee__contact__name', 'donee__contact__lastname']

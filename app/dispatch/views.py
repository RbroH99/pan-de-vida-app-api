"""
Views for the dispatch API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
)

from dispatch import serializers

from core. models import (
    Dispatch,
    DispatchItems,
    Item
)
from core.permissions import (
    IsNotDonor,
    IsColaboratorMinimun
)

from .filters import DispatchFilter


class BasePrivateModel(viewsets.ModelViewSet):
    """Basic view Authorization for name-only models."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsNotDonor]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]


class ItemViewSet(BasePrivateModel):
    """Viewset for the items."""
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    filterset_fields = ['category']
    search_fields = ["name"]
    ordering_fields = ['name']
    ordering = ['name', 'category']


class DispatchViewSet(BasePrivateModel):
    """Viewset for the dispatch objects."""
    queryset = Dispatch.objects.all()
    serializer_class = serializers.DispatchSerializer
    permission_classes = [IsAuthenticated, IsColaboratorMinimun]
    filterset_class = DispatchFilter
    search_fields = ['code', 'dispatcher__name', 'church__name', 'receiver']
    ordering_fields = ['date', 'code']
    ordering = ['date']

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.DispatchListSerializer
        return super().get_serializer_class()

    @action(methods=['get'], detail=False, url_path='filters-options')
    def filters_options(self, request, *args, **kwargs):
        """
        Returns a list of filters with their unique options from the database.
        """
        filters = {}
        filter_fields = []
        for filter in self.filterset_class.Meta.fields:
            filter_fields.append(filter) if "date" not in filter else None

        for filter in filter_fields:

            field = self.filterset_class.Meta.model._meta.get_field(
                filter.split("__", 1)[0]
            )

            if field.is_relation:
                related_model = field.related_model
                related_field_name = filter.split("__", 1)[1]
                distinct_values = (
                    related_model.objects.values_list(
                        related_field_name,
                        flat=True
                    )
                    .distinct()
                )
                filters[filter] = list(distinct_values)
            else:
                distinct_values = (
                    self.filterset_class.Meta.model.objects.values_list(
                        filter, flat=True
                    )
                    .distinct()
                )
                filters[filter] = list(distinct_values)

        for filter in self.filterset_class.Meta.fields:
            if "date" in filter:
                filters[filter] = []

        return Response(filters)


class DispatchItemViewSet(BasePrivateModel):
    """Viewset for the dispatch items objects."""
    queryset = DispatchItems.objects.all()
    serializer_class = serializers.DispatchItemSerializer
    permission_classes = [IsAuthenticated, IsColaboratorMinimun]
    filterset_fields = ['dispatch__code', 'stock']
    search_fields = [
        'item__name',
        'beneficiary__contact__name',
        'beneficiary__contact__lastname'
    ]
    ordering_fields = ['item__name']
    ordering = ['dispatch__date', 'item__name']

"""
Views for the dispatch API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend
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
    IsNotDonor
)


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
    filterset_fields = ['code', 'church__municipality__province']
    search_fields = ['code', 'dispatcher__name', 'church__name', 'receiver']
    ordering_fields = ['date', 'code']
    ordering = ['date']


class DispatchItemViewSet(BasePrivateModel):
    """Viewset for the dispatch items objects."""
    queryset = DispatchItems.objects.all()
    serializer_class = serializers.DispatchItemSerializer
    filterset_fields = ['dispatch__code', 'stock']
    search_fields = [
        'item__name',
        'beneficiary__contact__name',
        'beneficiary__contact__lastname'
    ]
    ordering_fields = ['item__name']
    ordering = ['dispatch__date', 'item__name']

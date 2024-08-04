"""
Viewsets for the church APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import (
    viewsets,
)

from church import serializers

from core.models import (
    Municipality,
    Denomination,
    Church
)


class BasePrivateViewSet(viewsets.ModelViewSet):
    """Base authorization classes viewset for private endpoints."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']


class MunicipalityViewSet(BasePrivateViewSet):
    """Viewset for the municipality."""
    serializer_class = serializers.MunicipalitySerializer
    queryset = Municipality.objects.all()


class DenominationViewSet(BasePrivateViewSet):
    """Viewset for the municipality."""
    serializer_class = serializers.DenominationSerializer
    queryset = Denomination.objects.all()
    filterset_fields = []


class ChurchViewSet(BasePrivateViewSet):
    """Viewset for the church endpoints."""
    serializer_class = serializers.ChurchDetailSerializer
    queryset = Church.objects.all()
    filterset_fields = BasePrivateViewSet.filterset_fields + [
        'denomination__name',
        'municipality__name',
        'municipality__province']

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ChurchSerializer

        return self.serializer_class

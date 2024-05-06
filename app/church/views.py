"""
Viewsets for the church APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
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


class MunicipalityViewSet(BasePrivateViewSet):
    """Viewset for the municipality."""
    serializer_class = serializers.MunicipalitySerializer
    queryset = Municipality.objects.all()


class DenominationViewSet(BasePrivateViewSet):
    """Viewset for the municipality."""
    serializer_class = serializers.DenominationSerializer
    queryset = Denomination.objects.all()


class ChurchViewSet(BasePrivateViewSet):
    """Viewset for the church endpoints."""
    serializer_class = serializers.ChurchDetailSerializer
    queryset = Church.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ChurchSerializer

        return self.serializer_class

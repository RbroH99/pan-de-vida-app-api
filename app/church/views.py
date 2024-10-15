"""
Viewsets for the church APP.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework import (
    viewsets,
    status,
)

from church import serializers

from core.models import (
    Municipality,
    Denomination,
    Church,
    Contact
)

from core.utils import PROVINCES_CUBA


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
    ordering_fields = ['name', 'denomination__name']

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ChurchSerializer

        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        priest = self.get_object().priest
        facilitator = self.get_object().facilitator
        if priest:
            Contact.delete(priest)
        if facilitator:
            Contact.delete(facilitator)
        return super().destroy(request, *args, **kwargs)


class ProvincesOptionsView(APIView):
    """View to get gender options. """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        provinces_choices = [
            {'label': choice[1], 'value': choice[0]}
            for choice in PROVINCES_CUBA
        ]
        return Response(provinces_choices, status=status.HTTP_200_OK)

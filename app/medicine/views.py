"""
Views for the medicine API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from medicine import serializers

from core. models import (
    MedClass,
)


class MedClassViewSet(viewsets.ModelViewSet):
    """Manage medicine classifications."""
    serializer_class = serializers.MedClassSerializer
    queryset = MedClass.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

"""
Serializers for the medicine API.
"""
from rest_framework import serializers

from core.models import (
    MedClass,
)


class MedClassSerializer(serializers.ModelSerializer):
    """Serializer fo the medclass endpoints."""

    class Meta:
        model = MedClass
        fields = ['id', 'name']
        read_only_fields = ['id']

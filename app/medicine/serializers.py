"""
Serializers for the medicine API.
"""
from rest_framework import serializers

from core.models import (
    MedClass,
    MedicinePresentation,
)


class BasicNameOnlyModelSerializer(serializers.ModelSerializer):
    """Serializer Meta for models that has only name attr."""

    class Meta:
        fields = ['id', 'name']
        read_only_fields = ['id']


class MedClassSerializer(BasicNameOnlyModelSerializer):
    """Serializer fo the medclass endpoints."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = MedClass


class MedicinePresentationSerializer(serializers.ModelSerializer):
    """Serializer fo the medclass endpoints."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = MedicinePresentation

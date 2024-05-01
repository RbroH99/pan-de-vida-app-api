"""
Serializers for the medicine API.
"""
from rest_framework import serializers

from core.utils import measurement_choices
from core.models import (
    MedClass,
    MedicinePresentation,
    Medicine
)


class BasicNameOnlyModelSerializer(serializers.ModelSerializer):
    """Serializer Meta for models that has only name attr."""

    class Meta:
        fields = ['id', 'name']
        read_only_fields = ['id']


class MedClassSerializer(BasicNameOnlyModelSerializer):
    """Serializer for the medclass endpoints."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = MedClass


class MedicinePresentationSerializer(serializers.ModelSerializer):
    """Serializer fo the medclass endpoints."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = MedicinePresentation


class MedicineSerializer(BasicNameOnlyModelSerializer):
    """Serializer for medicine endpoints."""
    presentation = MedicinePresentationSerializer(many=False, required=False)
    measurement_units = serializers.ChoiceField(choices=measurement_choices,
                                                default='-')

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = Medicine
        fields = BasicNameOnlyModelSerializer.Meta.fields + \
            ['presentation', 'measurement', 'measurement_units']


class MedicineDetailSerializer(MedicineSerializer):
    """Detail endpoint for medicine instances."""
    classification = MedClassSerializer(many=False, required=False)

    class Meta(MedicineSerializer.Meta):
        fields = MedicineSerializer.Meta.fields + \
              ['classification', 'batch']

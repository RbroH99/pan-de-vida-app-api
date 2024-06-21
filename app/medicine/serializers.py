"""
Serializers for the medicine API.
"""
from rest_framework import serializers

from django.http import JsonResponse

from core.utils import measurement_choices
from core.models import (
    MedClass,
    MedicinePresentation,
    Medicine,
    Disease,
    Treatment,
    Patient
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
    classification = MedClassSerializer(many=False, required=False)
    presentation = MedicinePresentationSerializer(many=False, required=False)
    measurement_units = serializers.ChoiceField(choices=measurement_choices,
                                                default='-')

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = Medicine
        fields = BasicNameOnlyModelSerializer.Meta.fields + \
            ['presentation', 'classification', 'measurement', 'measurement_units']


class MedicineDetailSerializer(MedicineSerializer):
    """Detail endpoint for medicine instances."""


    class Meta(MedicineSerializer.Meta):
        fields = MedicineSerializer.Meta.fields + \
              [ 'batch']


class DiseaseSerializer(BasicNameOnlyModelSerializer):
    """Serializer fr the disease object."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = Disease


class TreatmentSerializer(serializers.ModelSerializer):
    """Serializer for the treatments."""
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        required=True
    )
    disease = serializers.PrimaryKeyRelatedField(
        queryset=Disease.objects.all(),
        required=True)
    medicine = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Medicine.objects.all(),
        required=False
    )

    class Meta:
        model = Treatment
        fields = ['id', 'patient', 'disease', 'medicine']
        read_only_fields = ['id']

    def _get_set_medicines(self, medicines, treatment):
        """Get medicine id list and add it to the treatment."""
        invalid_meds = []
        for obj in medicines:
            try:
                medicine_id = obj.id
                medicine_obj = Medicine.objects.get(id=medicine_id)
                treatment.medicine.add(medicine_obj)
            except Medicine.DoesNotExist:
                invalid_meds.append(obj)

        if len(invalid_meds) > 0:
            return JsonResponse({'ivalid_meds': invalid_meds}, status=200)

    def create(self, validated_data):
        """Create new treatment instance in the DB."""
        meds = validated_data.pop('medicine', None)
        treatment = Treatment.objects.create(**validated_data)

        if meds:
            self._get_set_medicines(meds, treatment)

        return treatment

    def update(self, instance, validated_data):
        """Update treatment instances."""
        meds = validated_data.pop('medicine', None)

        if meds is not None:
            instance.medicine.clear()
            self._get_set_medicines(meds, instance)

        instance.save()
        return instance

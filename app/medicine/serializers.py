"""
Serializers for the medicine API.
"""
from rest_framework import serializers

from django.http import JsonResponse
from django.utils.translation import gettext as _

from core.utils import (
    measurement_choices,
    name_validator
)
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

    def validate_name(self, name):
        return name_validator(MedClass, name)

    def create(self, validated_data):
        name = validated_data.pop("name", None)

        classification = MedClass.objects.create(name=name)

        return classification


class MedicinePresentationSerializer(serializers.ModelSerializer):
    """Serializer fo the medclass endpoints."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = MedicinePresentation

    def validate_name(self, name):
        return name_validator(MedicinePresentation, name)

    def create(self, validated_data):
        name = validated_data.pop("name", None)

        presentation = MedicinePresentation.objects.create(name=name)

        return presentation



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

    def update(self, instance, validated_data):
        validated_data.pop("id", None)
        classification_data = validated_data.pop('classification', None)
        presentation_data = validated_data.pop('presentation', None)

        if classification_data:
            classification, _ = MedClass.objects.get_or_create(classification_data['name'])
            instance.classification = classification

        if presentation_data:
            presentation, _ = MedicinePresentation.objects.get_or_create()
            instance.presentation = presentation

        instance.name = validated_data.get("name", instance.name)
        instance.measurement = validated_data.get("measurement",
                                                  instance.measurement)
        instance.measurement_units = validated_data.\
            get("measurement_units", instance.measurement_units)

        instance.save()

        return instance


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

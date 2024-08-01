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
    Donee
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
            ['presentation', 'classification', 'measurement',
             'measurement_units', 'quantity']

    def nameonly_attr_validation(self, incoming_data, classname, model_class):
        """Validates nameonly attributes passed to medicine endpoint."""
        if incoming_data.get("id", None):
            try:
                obj = model_class.objects.get(id=incoming_data.get("id"))
                validated_data = {"name": obj.name}
                return validated_data
            except model_class.DoesNotExist:
                raise serializers.ValidationError(
                    f"{classname} {_('does not exist!')}"
                )
        name = incoming_data.get("name", None)
        if name:
            try:
                if type(name) is not str:
                    raise serializers.ValidationError(
                        _("Name must be a string!")
                    )
                else:
                    validated_data = {"name": name}
                    return validated_data
            except Exception as e:
                print(
                    f"{_('An exception ocurred:')} {e}, "
                    + f"{_('type:')}{type(name)}"
                    )

    def validate_classification(self, classification_data):
        """Validates classification passed to medicine endpoint."""
        validated_data = self.nameonly_attr_validation(
            classification_data,
            "classification",
            MedClass
        )
        return validated_data

    def validate_presentation(self, presentation_data):
        """Validates presentation passed to medicine endpoint."""
        validated_data = self.nameonly_attr_validation(
            presentation_data,
            "presentation",
            MedicinePresentation
        )
        return validated_data

    def handle_model_attr_data(self, data, model_class):
        """
        Handle data in presentation and classification.
        and verify type of data to return the name attr.
        """
        if isinstance(data, model_class):
            return data.name
        elif isinstance(data, dict):
            return data.get('name')
        else:
            return data

    def create(self, validated_data):
        """Creates a new medicine instance."""
        classification_data = validated_data.pop('classification', None)
        presentation_data = validated_data.pop('presentation', None)

        medicine = Medicine.objects.create(**validated_data)

        if classification_data:
            classification_name = self.handle_model_attr_data(
                classification_data,
                MedClass
            )
            classification, created = MedClass.objects.get_or_create(
                name=classification_name
            )
            medicine.classification = classification

        if presentation_data:
            presentation_name = self.handle_model_attr_data(
                presentation_data,
                MedicinePresentation
            )
            presentation, created = MedicinePresentation.objects.get_or_create(
                name=presentation_name
            )
            medicine.presentation = presentation

        medicine.save()

        return medicine

    def update(self, instance, validated_data):
        validated_data.pop("id", None)
        classification_data = validated_data.pop('classification', None)
        presentation_data = validated_data.pop('presentation', None)

        if classification_data:
            classification_name = self.handle_model_attr_data(
                classification_data,
                MedClass
            )
            classification, created = MedClass.objects.get_or_create(
                name=classification_name
            )
            instance.classification = classification

        if presentation_data:
            presentation_name = self.handle_model_attr_data(
                presentation_data,
                MedicinePresentation
            )
            presentation, created = MedicinePresentation.objects.get_or_create(
                name=presentation_name
            )
            instance.presentation = presentation

        instance.name = validated_data.get("name", instance.name)
        instance.measurement = validated_data.get(
            "measurement",
            instance.measurement
        )
        instance.measurement_units = validated_data.get(
            "measurement_units",
            instance.measurement_units
        )

        instance.quantity = validated_data.get(
            "quantity",
            instance.quantity
        )

        instance.save()

        return instance

    def to_representation(self, instance):
        """Returns medicine json excluding quantity if not admin."""
        representation = super().to_representation(instance)
        user = self.context['request'].user
        if user.role != 1:
            representation.pop("quantity", None)
        return representation


class DiseaseSerializer(BasicNameOnlyModelSerializer):
    """Serializer for the disease object."""

    class Meta(BasicNameOnlyModelSerializer.Meta):
        model = Disease


class DiseaseListSerializer(DiseaseSerializer):
    """Return diseases with treatments related to them."""
    treatments = serializers.SerializerMethodField()

    class Meta(DiseaseSerializer.Meta):
        fields = DiseaseSerializer.Meta.fields + ['treatments']

    def get_treatments(self, obj):
        """Return medicines used for the disease."""
        treatment_ids = Treatment.objects.filter(
            disease=obj
        ).values_list('medicine__id', flat=True)

        unique_medicines = Medicine.objects.filter(
            id__in=treatment_ids
        ).distinct()

        return MedicineSerializer(unique_medicines, many=True).data


class TreatmentSerializer(serializers.ModelSerializer):
    """Serializer for the treatments."""
    donee = serializers.PrimaryKeyRelatedField(
        queryset=Donee.objects.all(),
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
        fields = ['id', 'donee', 'disease', 'medicine']
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

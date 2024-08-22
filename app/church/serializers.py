"""
Serializers for the Church APP.
"""
from rest_framework import serializers

from django.utils import timezone

from core.utils import PROVINCES_CUBA
from core.models import (
    Municipality,
    Denomination,
    Church,
    Note,
    Contact
)
from contact.serializers import (
    ContactSerializer,
    NoteSerializer,
    DonorSerializer,
    BaseContactChildrenSerializer
)


class BaseNameOnlyModelSerializer(serializers.ModelSerializer):
    """Basic id-name only for models serializers."""

    class Meta:
        fields = ['id', 'name']
        read_only_fields = ['id']


class MunicipalitySerializer(BaseNameOnlyModelSerializer):
    """Serializer for the municipality model."""
    province = serializers.ChoiceField(choices=PROVINCES_CUBA,
                                       default='-')

    class Meta(BaseNameOnlyModelSerializer.Meta):
        model = Municipality
        fields = BaseNameOnlyModelSerializer.Meta.fields + ['province']

    def get_province(self, obj):
        return obj.get_province_display()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['province'] = next(
            (
                value for key,
                value in PROVINCES_CUBA if key == instance.province
            ),
            "Unknown"
        )

        return representation


class DenominationSerializer(BaseNameOnlyModelSerializer):
    """Serializer for the denomination objects."""

    class Meta(BaseNameOnlyModelSerializer.Meta):
        model = Denomination


class ChurchSerializer(BaseNameOnlyModelSerializer):
    """Serializer for the Church objects."""
    denomination = serializers.PrimaryKeyRelatedField(
        queryset=Denomination.objects.all(),
        required=True
    )
    municipality = MunicipalitySerializer(required=False)
    priest = ContactSerializer(read_only=False, required=False)
    inscript = serializers.DateField(required=False, format="%Y-%m-%d")

    class Meta(BaseNameOnlyModelSerializer.Meta):
        model = Church
        fields = BaseNameOnlyModelSerializer.Meta.fields + \
            ['priest',
             'denomination',
             'municipality',
             'inscript']

    def contact_validation(self, contact_info):
        """
        This method uses the contact validation of the DonorSerializer for
        the Donor model, from contact.serializers and validates contact.
        """
        return DonorSerializer.validate_contact(self, contact_info)

    def validate_priest(self, priest_info):
        """Validate priest info for the church."""
        return self.contact_validation(priest_info)

    def to_representation(self, obj):
        representation = super().to_representation(obj)

        representation["denomination"] = DenominationSerializer(
            obj.denomination
        ).data

        return representation


class ChurchDetailSerializer(ChurchSerializer):
    """Serializer for the detail church endpoint."""
    facilitator = ContactSerializer(read_only=False, required=False)
    note = NoteSerializer(required=False)

    class Meta(ChurchSerializer.Meta):
        fields = ChurchSerializer.Meta.fields + \
            ['facilitator',
             'note']

    def validate_facilitator(self, facilitator_info):
        """Validate facilitator info for the church."""
        return self.contact_validation(facilitator_info)

    def create(self, validated_data):
        """Create a new church instance."""
        municipality = validated_data.pop('municipality', None)
        note = validated_data.pop('note', None)
        inscript = validated_data.pop('inscript', None)
        priest = validated_data.pop('priest', None)
        facilitator = validated_data.pop('facilitator', None)

        if not inscript:
            inscript = timezone.now().date()
        if municipality:
            municipality, created = Municipality.objects.get_or_create(
                **municipality)
        if note:
            note, created = Note.objects.get_or_create(**note)

        church = Church.objects.create(
            **validated_data,
            municipality=municipality,
            note=note,
            inscript=inscript
        )

        if priest:
            if priest not in Contact.objects.all():
                priest_instance = BaseContactChildrenSerializer.\
                    _safe_create_contact(self, priest)
            else:
                priest_instance = priest
            church.priest = priest_instance

        if facilitator:
            if priest not in Contact.objects.all():
                facilitator_instance = BaseContactChildrenSerializer.\
                    _safe_create_contact(self, facilitator)
            else:
                facilitator_instance = facilitator
            church.facilitator = facilitator_instance

        church.save()

        return church

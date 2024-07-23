"""
Serializers for the contact API.
"""
from rest_framework import serializers

from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_countries.serializers import CountryFieldMixin

from core.models import (
    Note,
    Contact,
    PhoneNumber,
    WorkingSite,
    Medic,
    Donor,
    Donee,
    Church
)
from core.utils import (
    gender_choices
)

import re


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for the Note model."""

    class Meta:
        model = Note
        fields = ['id', 'note']
        read_only_fields = ['id']


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for the contact model."""
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        many=False,
        required=False
        )
    note = NoteSerializer(many=False, required=False)
    gender = serializers.ChoiceField(choices=gender_choices,
                                     default='-')

    class Meta:
        model = Contact
        fields = [
            'id',
            'name',
            'lastname',
            'gender',
            'user',
            'address',
            'note'
            ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Creates a new contact instance in db."""
        note = validated_data.pop('note', None)
        contact = Contact.objects.create(**validated_data)

        if note:
            note = Note.objects.create(**note)
            contact.note = note

        contact.save()

        return contact


class PhoneNumberSerializer(serializers.ModelSerializer):
    """Serializer for the PhoneNumber model."""
    contact = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Contact.objects.all(),
        required=True)

    class Meta:
        model = PhoneNumber
        fields = ['id', 'contact', 'number']
        read_only_field = ['id']
        extra_kwargs = {'number': {
                            'required': True,
                            'allow_null': False,
                            'allow_blank': False,
                                }
                        }

    def validate_number(self, number):
        """Validates the phone number."""
        pattern = re.compile(r'^\+(?:\d{1,3})?[\s-]?\d{1,14}$')
        if not pattern.match(number):
            msg = _("Invalid phone number.")
            raise serializers.ValidationError(msg)

        return number


class WorkingSiteSerializer(serializers.ModelSerializer):
    """Serializer for the working site model."""

    class Meta:
        model = WorkingSite
        fields = ['id', 'name']
        read_only_fiels = ['id']


class BaseContactChildrenSerializer(serializers.ModelSerializer):
    """Base serializer for diferent diferent contact types."""
    contact = ContactSerializer(read_only=False)

    class Meta:
        fields = ['id', 'contact']
        read_only_fields = ['id']

    def validate_contact(self, contact_info):
        note = contact_info.get("note", None)
        request = self.context["request"]

        if "id" in contact_info:
            try:
                get_object_or_404(Contact, id=contact_info['id'])
            except Contact.DoesNotExist:
                raise serializers.ValidationError(_("Contact do not exists."))
        elif request.method == 'POST':
            if "name" not in contact_info:
                raise serializers.ValidationError(_("Contact needs a name."))

        if note:
            if "id" in note:
                try:
                    Note.objects.get(id=note["id"])
                except Note.DoesNotExist:
                    raise serializers.ValidationError(
                        _("Note instance does not exists.")
                    )
            elif "note" not in note:
                raise serializers.ValidationError(_("Note needs a body."))

        if "gender" not in contact_info:
            contact_info["gender"] = '-'

        return contact_info

    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact', None)
        if contact_data:
            contact = instance.contact
            note = contact_data.pop("note", None)
            if note:
                note_instance = contact.note
                if note_instance:
                    note_instance.note = note["note"]
                    note_instance.save()
                else:
                    note_instance = Note.objects.create(note=note["note"])
                    contact.note = note_instance
                    contact.save()
            # Actualizar los atributos del contacto
            for attr, value in contact_data.items():
                setattr(contact, attr, value)
            contact.save()

        # Actualizar los atributos de la instancia
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def _safe_create_contact(self, contact):
        """Safely creates a contact instance from valid given dict."""
        note = contact.pop("note", None)
        if "id" in contact:
            contact_instance = Contact.objects.get(id=contact[id])
            if note:
                if "id" in note:
                    try:
                        note_instance = Note.objects.get()
                    except Note.DoesNotExist:
                        if "note" in note:
                            note_instance = Note.objects.create(
                                note=note["note"]
                            )
                        else:
                            raise serializers.ValidationError(
                                _("Invalid Note Object!!")
                            )
                    contact_instance.note = note_instance
                    contact_instance.save()
        else:
            contact_instance = Contact.objects.create(**contact)
            if note:
                if "id" in note:
                    raise serializers.ValidationError(
                        _("New contact's note must be new.")
                    )
                elif "note" not in note:
                    raise serializers.ValidationError(
                        _("Note needs to have content.")
                    )
                note_instance = Note.objects.create(note=note["note"])
                contact_instance.note = note_instance
        return contact_instance


class MedicSerializer(BaseContactChildrenSerializer):
    """Serializer for the medic object."""
    workingsite = WorkingSiteSerializer(read_only=False,
                                        required=False)

    class Meta(BaseContactChildrenSerializer.Meta):
        model = Medic
        fields = BaseContactChildrenSerializer.Meta.fields + \
            ['workingsite', 'specialty']

    def validate_workingsite(self, workingsite_info):
        if "name" not in workingsite_info:
            raise serializers.ValidationError(
                _("Working site contact must have a name.")
            )

        workingsite, created = WorkingSite.objects.get_or_create(
            name=workingsite_info['name'],
            defaults={"name": workingsite_info['name']}
        )

        return workingsite

    def create(self, validated_data):
        """Creates a new medic instance in db."""
        workingsite = validated_data.pop("workingsite", None)
        contact = validated_data.pop("contact")

        contact_instance = self._safe_create_contact(contact)

        medic = Medic.objects.create(
            contact=contact_instance,
            **validated_data
        )

        if workingsite:
            medic.workingsite = workingsite
            medic.save()

        return medic


class DonorSerializer(CountryFieldMixin, BaseContactChildrenSerializer):
    """Serializer for the donor objects."""

    class Meta(BaseContactChildrenSerializer.Meta):
        model = Donor
        fields = BaseContactChildrenSerializer.Meta.fields + \
            ['country', 'city']


class DoneeSerializer(BaseContactChildrenSerializer):
    """Serializer for donee objects."""
    code = serializers.SerializerMethodField()
    inscript = serializers.DateField(required=False, format="%Y-%m-%d")
    church = serializers.CharField(source='church.name', read_only=True)
    province = serializers.CharField(source='church.municipality.province',
                                     read_only=True)

    class Meta(BaseContactChildrenSerializer.Meta):
        model = Donee
        fields = BaseContactChildrenSerializer.Meta.fields + \
            ['code', 'ci', 'inscript', 'church', 'province']
        read_only_fields = ['id', 'code']

    def get_code(self, obj):
        return obj.code


class DoneeDetailSerializer(DoneeSerializer):
    """Serializer for donee objects."""
    church = serializers.PrimaryKeyRelatedField(
        queryset=Church.objects.all(),
        required=True
    )

    class Meta(BaseContactChildrenSerializer.Meta):
        model = Donee
        fields = BaseContactChildrenSerializer.Meta.fields + \
            ['code', 'ci', 'inscript', 'church']
        read_only_fields = ['id', 'code']

    def get_code(self, obj):
        return obj.code

    def create(self, validated_data):
        """Create a new Donee innstance."""
        inscript = validated_data.pop('inscript', None)
        contact = validated_data.pop('contact', None)

        contact_instance = self._safe_create_contact(contact)

        if not inscript:
            inscript = timezone.now().date()

        donee = Donee.objects.create(
            inscript=inscript,
            contact=contact_instance,
            **validated_data
        )

        return donee

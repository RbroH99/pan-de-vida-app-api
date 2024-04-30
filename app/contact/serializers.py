"""
Serializers for the contact API.
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

from core.models import (
    Note,
    Contact,
    PhoneNumber,
    WorkingSite,
    Medic,
    Donor
)

from django.utils.translation import gettext as _

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
    note = NoteSerializer(many=True, required=False)
    gender = serializers.ChoiceField(choices=Contact.gender_choices,
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
        if "id" in contact_info:
            try:
                contact = get_object_or_404(Contact, id=contact_info['id'])
            except Contact.DoesNotExist:
                raise serializers.ValidationError(_("Contact do not exists."))
            return contact
        elif "name" not in contact_info:
            raise serializers.ValidationError(_("Medic contact needs a name."))

        if "gender" not in contact_info:
            contact_info["gender"] = '-'
        contact = Contact.objects.create(**contact_info)
        return contact

    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact', None)
        if contact_data:
            contact = instance.contact
            # Actualizar los atributos del contacto
            for attr, value in contact_data.items():
                setattr(contact, attr, value)
            contact.save()

        # Actualizar los atributos de la instancia
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class MedicSerializer(serializers.ModelSerializer):
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


class DonorSerializer(BaseContactChildrenSerializer):
    """Serializer for the donor objects."""
    # Tengo que ver cómo serializar el CountryField

    class Meta(BaseContactChildrenSerializer.Meta):
        model = Donor
        fields = BaseContactChildrenSerializer.Meta.fields + \
            ['country', 'city']

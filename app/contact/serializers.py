"""
Serializers for the contact API.
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model

from core.models import (
    Note,
    Contact,
    PhoneNumber,
    WorkingSite
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
    gender = serializers.ChoiceField(choices=Contact.gender_choices)

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

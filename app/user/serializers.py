"""
Serializers for the user API.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'role']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}, }

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        if self.context["request"].user.is_authenticated:
            if self.context["request"].user.role != 1:
                validated_data['role'] = 3
        else:
            validated_data['role'] = 3

        user = get_user_model().objects.create_user(**validated_data)

        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        if self.context["request"].user.role != 1:
            validated_data.pop("role", None)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

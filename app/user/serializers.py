"""
Serializers for the user API.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_str

import jwt

from datetime import datetime, timedelta


User = get_user_model()


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


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for the users password reset requests"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")
        return value

    def generate_password_reset_token(self, user):
        expires_in = timedelta(hours=1)
        payload = {
            'user_id': user.id,
            'exp': (datetime.now() + expires_in).timestamp()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    def send_password_reset_email(self, request):
        token = self.generate_password_reset_token(self.user)
        reset_url = (
            f"http://localhost:3000/reset-password/{token}"
        )

        html_message = render_to_string(
            'password_reset_email.html',
            {
                'user': self.user,
                'reset_url': reset_url,
                'email': self.user.email
            }
        )

        send_mail(
            subject="Restablecer contraseña",
            message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            html_message=html_message,
            fail_silently=False
        )


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for users passwords reset."""
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            decoded_token = jwt.decode(
                force_str(data['token']),
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            self.user = User.objects.get(id=decoded_token['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise serializers.ValidationError("Invalid or expired token")
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")

        return data

    def save(self):
        password = self.validated_data['password']
        self.user.set_password(password)
        self.user.save()

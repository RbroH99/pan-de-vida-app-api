"""
Serializers for the user API.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_str
from core.models import Contact

import logging

import jwt

from datetime import datetime, timedelta


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    name = serializers.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'name', 'role']
        extra_kwargs = {'password': {
            'write_only': True,
            'min_length': 8,
            "required": False
            }, }

    def validate_password(self, value):
        """Validate password."""
        if len(value) < 8:
            raise serializers.ValidationError(
                'Password must be at least 8 characters long.'
            )
        return value

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        if self.context["request"].user.is_authenticated:
            if self.context["request"].user.role != 0:
                validated_data['role'] = 5
        else:
            validated_data['role'] = 5

        user = get_user_model().objects.create_user(**validated_data)

        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        if self.context["request"].user.role > 1:
            validated_data.pop("role", None)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation["status"] = instance.is_active
        try:
            contact = Contact.objects.get(user=instance)
            representation["contact"] = {"id":contact.id, "name": f"{contact.name} {contact.lastname}"}
        finally:
            return representation


# Church Staff user creation -----------------------------------
class EmailConfirmationMessageSerializer(serializers.Serializer):
    """Serializer for sending email confirmation to users."""

    def generate_confirmation_token(self, user):
        expires_in = timedelta(days=1)
        payload = {
            'user_id': user.id,
            'exp': (datetime.now() + expires_in).timestamp()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    def send_confirmation_email(self, user):
        token = self.generate_confirmation_token(user)
        confirmation_url = (
            f"https://breadoflife.onrender.com/reset-password/{token}"
        )

        html_message = render_to_string(
            'email_confirmation.html',
            {
                'user': user,
                'confirmation_url': confirmation_url,
                'email': user.email
            }
        )

        send_mail(
            subject="Confirma tu cuenta",
            message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

    def save(self):
        self.user.is_active = True
        self.user.save()


class SetPasswordSerializer(serializers.Serializer):
    """Serializer for setting user's password."""
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
        except jwt.ExpiredSignatureError:
            if self.user:
                EmailConfirmationMessageSerializer.send_confirmation_email(
                    self.user
                )
            raise serializers.ValidationError("Expired token", code="EXPIRED")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token")
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")

        return data

    def save(self):
        password = self.validated_data['password']
        self.user.set_password(password)
        self.user.is_active = True
        self.user.save()


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for the church staff user object."""
    contact = serializers.IntegerField()

    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'role', 'contact']
        extra_kwargs = {}

    def create(self, validated_data):
        """Create and return a new user without password."""
        role = validated_data.get("role", None)
        contactId = self.validated_data.get("contact", None)
        contact = None
        logging.info(validated_data)

        if contactId:
            try:
                contact = Contact.objects.get(id=contactId)
            except Contact.DoesNotExist:
                logging.error("Contact does not exist, user will be created without contact associated.")

        if role:
            if role==1:
                raise serializers.ValidationError(
                        "Role not allowed trough this endpoint!"
                    )
            elif role < 2 and self.context["request"].user.role != 0:
                    raise PermissionDenied(
                        "Insuficient permission to create users with that role!"
                    )
            elif role == 5:
                if self.context["request"].user.role > 1:
                    raise serializers.ValidationError(
                        "Insuficient permission to create user with this role!"
                    )

        user = get_user_model().objects.create_user(
            password=None, is_active=False, **validated_data
        )

        if contact is not None:
            contact.user = user
            contact.save()

        EmailConfirmationMessageSerializer().send_confirmation_email(user)

        return user


# Password reset ------------------------------------------------
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
            f"https://breadoflife.onrender.com/reset-password/{token}"
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

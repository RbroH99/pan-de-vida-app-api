"""
Models for the pandevida app API.
"""
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class UserManager(BaseUserManager):
    """Manager for the users."""

    def create_user(self, id, email, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email!.')
        if not id:
            raise ValueError('User must have an id!.')
        email = self.normalize_email(email)
        user = self.model(id=id, email=email, **extra_fields)
        user.save(using=self._db)

        return user

    def create_superuser(self, id, email):
        """Create superuser with given details."""
        user = self.model(id=id, email=email)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """User in the API"""
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class MedClass(models.Model):
    """Medicine classification model."""
    name = models.CharField(max_length=60,
                            unique=True,
                            null=False,
                            blank=False)

    def __str__(self) -> str:
        return self.name


class MedicinePresentation(models.Model):
    """Medicine presentation model."""
    name = models.CharField(max_length=60,
                            unique=True,
                            null=False,
                            blank=False)

    def __str__(self) -> str:
        return self.name

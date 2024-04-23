"""
Models for the pandevida app API.
"""
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from django.utils.translation import gettext_lazy as _

from django.conf import settings


# USER RELATED MODELS
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
# --------------------------------------------------------------------


# MEDICINE APP RELATED MODELS
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


class Medicine(models.Model):
    """Medicine object in db."""
    measurement_choices = (
        ('mL', _('Milliliters')),
        ('oz', _('Ounce')),
        ('pt', _('Pint')),
        ('L', _('Liter')),
        ('mg', _('Milligram')),
        ('g', _('Gram')),
        ('lb', _('Pound')),
        ('-', _('Not Set'))
    )

    name = models.CharField(max_length=60,
                            blank=False,
                            null=False
                            )
    classification = models.ForeignKey(MedClass,
                                       null=True,
                                       blank=True,
                                       on_delete=models.SET_NULL
                                       )
    presentation = models.ForeignKey(MedicinePresentation,
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL
                                     )
    batch = models.CharField(max_length=30, blank=True, null=True)
    measurement = models.DecimalField(max_digits=5,
                                      decimal_places=2,
                                      null=True,
                                      blank=True
                                      )
    measurement_units = models.CharField(max_length=2,
                                         choices=measurement_choices,
                                         default='-'
                                         )

    def __str__(self) -> str:
        return f'Name: {self.name}, Batch: {self.batch}'
# -----------------------------------------------------------------------


# CONTACT APP RELATED MODELS
class Note(models.Model):
    """Notes and observation for object instances in the DB."""
    note = models.TextField()

    def __str__(self) -> str:
        return f'Note No.: {self.id}.'


class Contact(models.Model):
    """Contact info for persons in the db."""
    gender_choices = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('-', _('Other or not set'))
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=40, blank=False, null=False)
    lastname = models.CharField(max_length=40, blank=True, null=True)
    gender = models.CharField(max_length=1,
                              choices=gender_choices,
                              default='-'
                              )
    address = models.CharField(max_length=255, blank=True, null=True)
    note = models.ForeignKey(Note,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)

    def __str__(self) -> str:
        return f'{self.name} {self.lastname}'


class PhoneNumber(models.Model):
    """Phone number for contact."""
    contact = models.ForeignKey(Contact,
                                on_delete=models.CASCADE,
                                blank=False,
                                null=False)
    number = models.CharField(max_length=16,
                              unique=True,
                              blank=False,
                              null=False)

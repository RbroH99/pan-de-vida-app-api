"""
Models for the pandevida app API.
"""
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from django_countries.fields import CountryField

from .utils import (
    PROVINCES_CUBA,
    measurement_choices,
    gender_choices,
)


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


class Disease(models.Model):
    """Diseases pacients suffer."""
    name = models.CharField(max_length=80,
                            blank=False,
                            null=False)

    def __str__(self) -> str:
        return self.name


class Treatment(models.Model):
    """Medic treatment for pacient-illnesses."""
    patient = models.ForeignKey('Patient',
                                blank=False,
                                null=False,
                                on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease,
                                blank=False,
                                null=False,
                                on_delete=models.CASCADE)
    medicine = models.ManyToManyField(Medicine,
                                      blank=True)

    def __str__(self) -> str:
        return f'{str(self.patient)}, {self.disease.name}'
# -----------------------------------------------------------------------


# CONTACT APP RELATED MODELS
class Note(models.Model):
    """Notes and observation for object instances in the DB."""
    note = models.TextField()

    def __str__(self) -> str:
        return f'Note No.: {self.id}.'


class Contact(models.Model):
    """Contact info for persons in the db."""
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
                             on_delete=models.SET_NULL,
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


class WorkingSite(models.Model):
    """Working site for the medics."""
    name = models.CharField(max_length=70, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Medic(models.Model):
    """Medic contact in the system."""
    contact = models.OneToOneField(Contact,
                                   null=False,
                                   blank=False,
                                   on_delete=models.CASCADE)
    workingsite = models.ForeignKey(WorkingSite,
                                    blank=True,
                                    null=True,
                                    on_delete=models.SET_NULL
                                    )
    specialty = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.contact.name}: {self.specialty}'


class Donor(models.Model):
    """Donor in the system."""
    contact = models.ForeignKey(Contact,
                                on_delete=models.CASCADE,
                                blank=False,
                                null=False)
    country = CountryField(null=True, blank=True)
    city = models.CharField(max_length=45,
                            null=True,
                            blank=True)

    def __str__(self) -> str:
        return f'{self.contact.name}: {self.city}'


class Patient(models.Model):
    """Patients in the system."""
    code = models.CharField(max_length=12, unique=True, editable=False)
    contact = models.OneToOneField(Contact,
                                   null=False,
                                   blank=False,
                                   on_delete=models.CASCADE)
    ci = models.CharField(max_length=11,
                          blank=False,
                          null=False,
                          unique=True)
    inscript = models.DateField(default=timezone.now)
    church = models.ForeignKey('Church',
                               blank=False,
                               null=False,
                               on_delete=models.CASCADE)

    def generate_code(self):
        """Generate unique code for pacient from church id."""
        last_patient = \
            Patient.objects.filter(church=self.church)\
            .order_by('-code').first()
        if last_patient:
            try:
                last_specific_id = str(last_patient.code).split('-')[-1]
                code = f'{self.church.id}-{int(last_specific_id) + 1}'
            except (ValueError, IndexError):
                code = f'{self.church.id}-1'
        else:
            code = f'{self.church.id}-1'

        return code

    def save(self, *args, **kwargs):
        self.code = self.generate_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Patient: {self.code}'
# -----------------------------------------------------------------------


# CHURCH APP RELATED MODELS
class Municipality(models.Model):
    """Municipality of given provinces."""
    name = models.CharField()
    province = models.CharField(
        max_length=3,
        choices=PROVINCES_CUBA,
        default='UNK')

    def __str__(self) -> str:
        return f'{self.name}, {self.province}'


class Denomination(models.Model):
    """Denomination of the churchs."""
    name = models.CharField(max_length=60,
                            unique=True,
                            blank=False,
                            null=False)

    def __str__(self) -> str:
        return self.name


class Church(models.Model):
    """Church objects in the System."""
    name = models.CharField(max_length=60,
                            blank=False,
                            null=False)
    denomination = models.ForeignKey(Denomination,
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    priest = models.ForeignKey(Contact,
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL,
                               related_name='church_priest')
    facilitator = models.ForeignKey(Contact,
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name='church_facilitator')
    note = models.ForeignKey(Note,
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    municipality = models.ForeignKey(Municipality,
                                     blank=True,
                                     null=True,
                                     on_delete=models.SET_NULL)
    inscript = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.name}, {self.denomination.name}'

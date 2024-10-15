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
    role_choices
)


class Note(models.Model):
    """Notes and observation for object instances in the DB."""
    note = models.TextField()

    def __str__(self) -> str:
        return f'Note No.: {self.id}.'


# USER RELATED MODELS
class UserManager(BaseUserManager):
    """Manager for the users."""

    def create_unique_name_from_email(email):
        """Creates a unique name from email."""
        base_name = email.split('@')[0]
        name = base_name
        i = 1
        while User.objects.filter(name=name).exists():
            name = f'{base_name}{i}'
            i += 1
        return name

    def create_user(self, email, password=None, **extra_fields) -> 'User':
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email!.')
        email = self.normalize_email(email)
        role = extra_fields.pop("role", 5)
        user = self.model(email=email, role=role, **extra_fields)

        if not password:
            raise ValueError('Password must be provided!')
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, name='') -> 'User':
        """Create superuser with given details."""
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email)

        if name:
            user.name = name
        user.is_superuser = True
        user.is_staff = True
        user.role = 1
        if not password:
            raise ValueError('Password must be provided!')
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_church_staffuser(
            self, email, password, role=4, name=''
            ) -> 'User':
        """Create staffuser of church with given details."""
        if email:
            email = self.normalize_email(email)
            user = self.model(email=email)
            if not name:
                name = self.create_unique_name_from_email(email)

        if name:
            user.name = name
        user.is_staff = False
        if role not in [4, 5]:
            raise ValueError(
                'Only priest and facilitators can be created with this method!'
                )
        user.role = role
        if not password:
            raise ValueError('Password must be provided!')
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.PositiveSmallIntegerField(
        choices=role_choices,
        blank=True,
        null=True,
        default=5
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        """Returns the user string representation."""
        return self.email

# --------------------------------------------------------------------


# MEDICINE APP RELATED MODELS
class MedClass(models.Model):
    """Medicine classification model."""
    name = models.CharField(max_length=60,
                            null=False,
                            blank=False)

    def __str__(self) -> str:
        return self.name


class MedicinePresentation(models.Model):
    """Medicine presentation model."""
    name = models.CharField(max_length=60,
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
    measurement = models.DecimalField(max_digits=5,
                                      decimal_places=2,
                                      null=True,
                                      blank=True
                                      )
    measurement_units = models.CharField(max_length=2,
                                         choices=measurement_choices,
                                         default='-'
                                         )
    quantity = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f'Name: {self.name}, Quantity: {self.quantity}'


class Disease(models.Model):
    """Diseases donees suffer."""
    name = models.CharField(
        max_length=80,
        blank=False,
        null=False)

    def __str__(self) -> str:
        return self.name


class Treatment(models.Model):
    """Medic treatment for donees-illnesses."""
    donee = models.ForeignKey(
        'Donee',
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
        return f'{str(self.donee)}, {self.disease.name}'
# -----------------------------------------------------------------------


# CONTACT APP RELATED MODELS
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
    label = models.CharField(max_length=30,
                             blank=False,
                             null=False,
                             default="Sin Etiqueta")
    description = models.CharField(max_length=120,
                                   blank=True,
                                   null=True)


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


class Donee(models.Model):
    """Donees in the system."""
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

    def increment_number(self, code):
        """Increment specific number in code."""
        parts = code.split('-')
        current_number = int(parts[-1])
        new_number = current_number + 1
        return '-'.join(parts[:-1] + [str(new_number)])

    def generate_code(self):
        """Generate unique code for donee in its church."""
        last_donee = Donee.objects.filter(
            church=self.church
        ).order_by('-id').first()
        if last_donee:
            try:
                last_specific_id = str(last_donee.code).split('-')[-1]
                potential_code = \
                    f'{self.church.id}-{int(last_specific_id) + 1}'
            except (ValueError, IndexError):
                potential_code = f'{self.church.id}-1'
        else:
            potential_code = f'{self.church.id}-1'

        while True:
            if not Donee.objects.filter(code=potential_code).exists():
                break
            potential_code = self.increment_number(potential_code)

        return potential_code

    def save(self, *args, **kwargs):
        self.code = self.generate_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Donee: {self.code}'
# -----------------------------------------------------------------------


# CHURCH APP RELATED MODELS
class Municipality(models.Model):
    """Municipality of given provinces."""
    name = models.CharField(max_length=60)
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
    priest = models.OneToOneField(Contact,
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='church_priest')
    facilitator = models.OneToOneField(Contact,
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

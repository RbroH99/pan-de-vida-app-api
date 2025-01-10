"""
Models for the pandevida app API.
"""
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError

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

    def create_unique_name_from_email(self, email):
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
            user.is_active = False
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
        user.role = 0
        if not password:
            raise ValueError('Password must be provided!')
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_church_staffuser(
            self, email, password=None, role=4, name=''
            ) -> 'User':
        """Create staffuser of church with given details."""
        if email:
            email = self.normalize_email(email)
            user = self.create_user(email=email)
            if not name:
                name = self.create_unique_name_from_email(email)

        if name:
            user.name = name
        user.is_staff = False
        if role not in [3, 4]:
            raise ValueError(
                'Only priest and facilitators can be created with this method!'
                )
        user.role = role
        if not password:
            user.is_active = False
        else:
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
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}-{self.presentation.name if self.presentation else ""} {self.measurement}{self.measurement_units}' # noqa


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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'province'],
                name='unique_municipality_province')
        ]

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
                                     on_delete=models.SET_NULL,)
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
        denomination_name = self.denomination.name if self.denomination else ""
        return f'{self.name}, {denomination_name}'

# ----------------------------------------------------------------------------

# ARTICLE RELATED MODELS


class Item(models.Model):
    """Articles other than medicines."""
    name = models.CharField(max_length=150, blank=False, null=False)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    category = models.CharField(
        max_length=60,
        default="unknown",
        blank=True,
        null=True,
        unique=True,
    )

    def clean_category(self):
        self.category = str(self.category).lower()

    def __str__(self):
        return self.name

# ----------------------------------------------------------------------------

# DISPATCH RELATED MODELS


class Dispatch(models.Model):
    """Dispatch object, emitted for churchs."""
    code = models.CharField(max_length=20, unique=True)
    church = models.ForeignKey(Church, on_delete=models.PROTECT)
    dispatcher = models.ForeignKey(
        get_user_model(),
        max_length=200,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )
    date = models.DateTimeField(default=timezone.now)
    receiver = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = _('Dispatch')
        verbose_name_plural = _("Dispatches")

    def generate_code(self):
        current_date = self.date
        year = current_date.year
        month = current_date.month
        day = current_date.day

        base_code = \
            f"D{day:02d}{month:02d}{year % 100:02d}I{self.church.id:03d}"

        if Dispatch.objects.filter(code__startswith=base_code).exists():
            existing_dispatches = Dispatch.objects.filter(
                code__startswith=base_code
            )
            next_number = int(
                existing_dispatches.order_by("code").last().code[-2:]
            ) + 1
            self.code = f"{base_code}-{next_number:02d}"
        else:
            self.code = base_code

    def save(self, *args, **kwargs):
        self.generate_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Dispatch {self.code} - Church: {self.church}'


class DispatchItems(models.Model):
    """
    Items allotted for a church on a dispatch,
    if stock is true can't have a beneficiary.
    """
    dispatch = models.ForeignKey(
        Dispatch,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ['medicine', 'item']
            },
        blank=False,
        null=False
        )
    object_id = models.PositiveIntegerField(blank=False, null=False)
    item = GenericForeignKey('content_type', 'object_id')
    quantity = models.IntegerField()
    beneficiary = models.ForeignKey(
        Donee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    stock = models.BooleanField(default=False)
    observation = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Dispatch Item')
        verbose_name_plural = _("Dispatch Items")

    def __str__(self):
        return f'{self.item} - Quantity: {self.quantity}'

    def validate_stock_beneficiary(self):
        """Validates the relation between stock and beneficiary."""
        if self.beneficiary is not None and self.stock:
            raise ValidationError(
                {"stock": "Stock can't have a beneficiary."}
            )
        elif not self.stock and self.beneficiary is None:
            message = "If item is not stock, it must have a beneficiary."
            raise ValidationError(
                {"beneficiary": message},
                'invalid beneficiary-stock relation'
            )

    def save(self, *args, **kwargs):
        """Custom save method to apply clean before model save."""
        self.validate_stock_beneficiary()
        return super().save(*args, **kwargs)

# -----------------------------------------------------------------------

# ANNOUNCEMNETS RELATED MODELS


class Announcement(models.Model):
    """Announcement object."""
    title = models.CharField(max_length=150, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    date = models.DateTimeField(default=timezone.now)
    initial_date = models.DateTimeField(blank=True, null=True)
    final_date = models.DateTimeField(blank=True, null=True)
    directed_to = models.JSONField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def clean(self):
        if self.initial_date and self.final_date:
            if self.initial_date > self.final_date:
                message = "Initial date can't be after final date."
                raise ValidationError(
                    {
                        "initial_date": message
                    }
                )
        allowed_roles = range(0, 6)
        if self.directed_to:
            if not all(role in allowed_roles for role in self.directed_to):
                raise ValidationError({
                    "directed_to": "One or more roles are invalid."
                })
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        return super().clean()

    def __str__(self):
        return f'{self.title}-{self.date.date()}'

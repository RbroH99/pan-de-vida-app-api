"""
Utils needed in the core app.
"""
from django.utils.translation import gettext as _

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenGenerator(RefreshToken):
    @classmethod
    def _get_validated_token(cls, user):
        """
        Override this method to add custom claims to the token.
        """
        token = cls.for_user(user)
        return token.access_token

    @classmethod
    def get_token(cls, user):
        """
        Returns a valid token for a user with a given username.
        """
        token = cls._for_user_claims(user)
        return token

    @classmethod
    def _for_user_claims(cls, user):
        """
        Create a new token instance and populate the default claims
        by calling the constructor.
        """
        token = cls()
        if user is None:
            raise ValueError("Usuario no encontrado.")
        token.payload["role"] = user.role
        return token


role_choices = (
    (0, 'admin'),
    (1, 'colaborator'),
    (2, 'agent'),
    (3, 'priest'),
    (4, 'facilitator'),
    (5, 'donor'),
)

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


gender_choices = (
    ('-', _('Other or not set')),
    ('M', _('Male')),
    ('F', _('Female'))
)


PROVINCES_CUBA = (
    ('PRI', 'Pinar del Río'),
    ('ART', 'Artemisa'),
    ('HAB', 'La Habana'),
    ('MAY', 'Mayabeque'),
    ('MTZ', 'Matanzas'),
    ('CFG', 'Cienfuegos'),
    ('VCL', 'Villa Clara'),
    ('SSP', 'Sancti Spíritus'),
    ('CAV', 'Ciego de Ávila'),
    ('CMG', 'Camagüey'),
    ('LTU', 'Las Tunas'),
    ('GRA', 'Granma'),
    ('HOL', 'Holguín'),
    ('SCU', 'Santiago'),
    ('GTM', 'Guantánamo'),
    ('IJV', 'Isla de la Juventud'),
    ('UNK', _('UNKNOWN'))
)


def name_validator(model_ref, name):
    names_list = model_ref.objects.all().values("name")
    if name in names_list:
        raise serializers.ValidationError(
            ("Name already exists in the DB."),
            code='unique'
        )
    return name

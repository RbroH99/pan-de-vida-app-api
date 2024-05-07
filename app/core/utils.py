"""
Utils needed in the core app.
"""
from django.utils.translation import gettext as _


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
    ('M', _('Male')),
    ('F', _('Female')),
    ('-', _('Other or not set'))
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

"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login', 'email']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        """
        Override original method and return False, preventing admin users
        on change passwords through Main API.
        """
        return False


admin.site.register(models.UserProfile, UserAdmin)
admin.site.register(models.Denomination)
admin.site.register(models.MedClass)
admin.site.register(models.MedicinePresentation)
admin.site.register(models.Medicine)
admin.site.register(models.Contact)
admin.site.register(models.Church)
admin.site.register(models.Donor)
admin.site.register(models.Disease)
admin.site.register(models.Patient)
admin.site.register(models.Treatment)
admin.site.register(models.WorkingSite)
admin.site.register(models.Municipality)
admin.site.register(models.Note)
admin.site.register(models.PhoneNumber)

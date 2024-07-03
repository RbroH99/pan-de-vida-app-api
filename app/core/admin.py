"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    model = models.User
    ordering = ['id']
    list_display = ['email', 'name']
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
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    def save_form(self, request, form, change):
        if form.cleaned_data.get('is_superuser'):
            form.instance = self.model.objects.create_superuser(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                name=form.cleaned_data['name'],
            )
        else:
            form.instance = self.model.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                name=form.cleaned_data['name'],
            )
        return super().save_form(request, form, change)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Denomination)
admin.site.register(models.MedClass)
admin.site.register(models.MedicinePresentation)
admin.site.register(models.Medicine)
admin.site.register(models.Medic)
admin.site.register(models.Contact)
admin.site.register(models.Church)
admin.site.register(models.Donor)
admin.site.register(models.Disease)
admin.site.register(models.Donee)
admin.site.register(models.Treatment)
admin.site.register(models.WorkingSite)
admin.site.register(models.Municipality)
admin.site.register(models.Note)
admin.site.register(models.PhoneNumber)

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
        (None, {'fields': ('email', 'password', "name")}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'role',
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
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """Save the model using the appropriate logic."""
        if not change:
            # Create new user or superuser based on the form input
            if form.cleaned_data.get('is_superuser'):
                obj = self.model.objects.create_superuser(
                    email=form.cleaned_data.get('email'),
                    password=form.cleaned_data.get('password1'),
                    name=form.cleaned_data.get('name'),
                )
            else:
                obj = self.model.objects.create_user(
                    email=form.cleaned_data.get('email'),
                    password=form.cleaned_data.get('password1'),
                    name=form.cleaned_data.get('name')
                )
        else:
            # Update an existing user
            obj.email = form.cleaned_data.get('email')
            obj.name = form.cleaned_data.get('name')
            obj.is_active = form.cleaned_data.get('is_active', obj.is_active)
            obj.is_staff = form.cleaned_data.get('is_staff', obj.is_staff)
            obj.is_superuser = form.cleaned_data.get(
                'is_superuser', obj.is_superuser
            )
            obj.role = form.cleaned_data.get('role', obj.role)

            # Update password only if provided
            password = form.cleaned_data.get('password1')
            if password:
                obj.set_password(password)

            obj.save()

        return obj

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
admin.site.register(models.Dispatch)
admin.site.register(models.DispatchItems)
admin.site.register(models.Item)

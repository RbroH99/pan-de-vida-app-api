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

    def save_model(self, request, instance, change):
        if not change:
            if request.POST.get('is_superuser'):
                instance = self.model.objects.create_superuser(
                    email=request.POST.get('email'),
                    password=request.POST.get('password1'),
                    name=request.POST.get('name'),
                )
            else:
                instance = self.model.objects.create_user(
                    email=request.POST.get('email'),
                    password=request.POST.get('password1'),
                    name=request.POST.get('name')
                )
        else:
            for key, value in request.POST.items():
                if 'password' not in key:
                    setattr(instance, key, value)
                else:
                    instance.set_password(key)
            instance.save()

        return instance


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

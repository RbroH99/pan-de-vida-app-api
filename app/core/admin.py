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

    # def save_model(self, request, obj, form, change):
    #     if not change:
    #         if request.POST.get('is_superuser'):
    #             obj = self.model.objects.create_superuser(
    #                 email=request.POST.get('email'),
    #                 password=request.POST.get('password1'),
    #                 name=request.POST.get('name'),
    #             )
    #         else:
    #             obj = self.model.objects.create_user(
    #                 email=request.POST.get('email'),
    #                 password=request.POST.get('password1'),
    #                 name=request.POST.get('name')
    #             )
    #     else:
    #         for key, value in request.POST.items():
    #             if type(value) is str:
    #                 if value.lower() == 'true' or value.lower() == 'false':
    #                     if value.lower() == 'true':
    #                         value = True
    #                     elif value.lower() == 'false':
    #                         value = False
    #             if 'password' not in key:
    #                 setattr(obj, key, value)
    #             else:
    #                 obj.set_password(key)
    #         obj.save()

    #     return obj


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

"""
Django admin configuration for the NewsApplication.

Registers Article, Newsletter, Publisher, and CustomUser models
with the admin site and extends the UserAdmin to include the role field.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Article, Newsletter, Publisher


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the CustomUser model.

    Extends the default UserAdmin to expose the ``role`` field
    in both the user edit and user creation interfaces.
    """

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Role Assignment", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Role Assignment", {"fields": ("role",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Publisher)

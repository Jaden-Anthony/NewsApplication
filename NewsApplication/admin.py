from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Article, Newsletter, Publisher


# Registering the custom user model requires UserAdmin for password hashing compatibility
class CustomUserAdmin(UserAdmin):
    # 1. Injects the 'role' field into the User Edit interface
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Role Assignment", {"fields": ("role",)}),
    )

    # 2. Injects the 'role' field into the User Creation interface
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Role Assignment", {"fields": ("role",)}),
    )


# Register CustomUser ONLY ONCE using the newly defined CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)

# Register the rest of the models
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Publisher)

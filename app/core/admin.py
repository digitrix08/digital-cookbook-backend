from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.translation import gettext as _


# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal details"), {"fields": ("name",)}),
        (_("Important Dates"), {"fields": ("last_login",)}),
        (_("Permission"), {"fields": (
            "is_staff",
            "is_superuser",
            "is_active"
        )})
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2")
        }),
    )


admin.site.register(User, UserAdmin)

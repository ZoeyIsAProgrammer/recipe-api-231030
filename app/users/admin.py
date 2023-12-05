from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin


class UserAdmin(UserAdmin):
    ordering = ["id"]
    list_display = ["email", "name", "id"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


admin.site.register(CustomUser, UserAdmin)

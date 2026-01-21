from django.contrib import admin

from apps.core.admin_mixins import TenantAdminMixin

from .models import Role, User


@admin.register(User)
class UserAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("nom", "prenom", "email", "role", "status", "created_at")
    list_filter = ("status", "role")
    search_fields = ("email", "nom", "prenom")
    readonly_fields = ("last_login", "created_at", "updated_at")

    fieldsets = (
        ("Identité", {"fields": ("email", "nom", "prenom", "profile")}),
        ("Organisation", {"fields": ("entreprise", "role", "status")}),
        ("Sécurité", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.entreprise and not request.user.is_superuser:
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass

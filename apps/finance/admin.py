from django.contrib import admin

from apps.core.admin_mixins import TenantAdminMixin

from .models import Depense


@admin.register(Depense)
class DepenseAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("type", "montant",  "created_at")
    list_filter = ("type",)

    def save_model(self, request, obj, form, change):
        if not obj.entreprise and not request.user.is_superuser:
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)

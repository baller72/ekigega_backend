from django.contrib import admin

from apps.core.admin_mixins import TenantAdminMixin

from .models import Produit, Vente


@admin.register(Produit)
class ProduitAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("nom", "categorie", "prix", "quantite")
    search_fields = ("nom",)
    list_filter = ("categorie",)

    def save_model(self, request, obj, form, change):
        if not obj.entreprise and not request.user.is_superuser:
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)


@admin.register(Vente)
class VenteAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("client", "statut", "created_at")
    list_filter = ("statut",)

    def save_model(self, request, obj, form, change):
        if not obj.entreprise and not request.user.is_superuser:
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)

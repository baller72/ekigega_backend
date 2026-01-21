from django.contrib import admin

from .models import Abonnement


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    pass

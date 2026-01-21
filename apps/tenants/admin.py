from django.contrib import admin

from .models import Entreprise


# Register your models here.
@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    pass

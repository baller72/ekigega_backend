from django.contrib import admin
from .models import ExportHistory

@admin.register(ExportHistory)
class ExportHistoryAdmin(admin.ModelAdmin):
    pass
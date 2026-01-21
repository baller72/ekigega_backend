from django.contrib import admin

from apps.logs.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "entreprise",
        "user",
        "action",
        # "user_agent",
        "status_code",
        "ip_address",
    )

    list_filter = ("action", "status_code", "entreprise")
    search_fields = ("user__email", "path", "ip_address")
    readonly_fields = [field.name for field in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

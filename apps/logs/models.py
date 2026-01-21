from django.db import models

from apps.core.models import BaseModel


class AuditLog(BaseModel):
    entreprise = models.ForeignKey(
        "tenants.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    action = models.CharField(max_length=50, db_index=True)
    method = models.CharField(max_length=10, db_index=True)
    path = models.CharField(max_length=255)

    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    status_code = models.PositiveSmallIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "created_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.action} - {self.user}"

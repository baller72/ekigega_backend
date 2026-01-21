from django.db import models
from apps.core.models import BaseModel, TenantModel
from apps.accounts.models import User

class ExportHistory(TenantModel):
    MODULE_CHOICES = [
        ("Ventes", "Ventes"),
        ("Produits", "Produits"),
        ("Depenses", "Dépenses"),
        ("Abonnements", "Abonnements"),
    ]

    FORMAT_CHOICES = [
        ("CSV", "CSV"),
        ("Excel", "Excel"),
        ("PDF", "PDF"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_url = models.FileField(upload_to="exports/")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.module} ({self.format}) - {self.created_at}"
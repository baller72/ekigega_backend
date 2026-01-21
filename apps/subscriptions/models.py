from django.db import models

from apps.core.models import BaseModel, TenantModel


class Abonnement(TenantModel):
    STATUS = [
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    TYPES = [
        ("basic", "BASIC"),
        ("medium", "MEDIUM"),
        ("premium", "PREMIUM"),
    ]

    type = models.CharField(max_length=50, choices=TYPES, db_index=True)
    date_debut = models.DateField(db_index=True)
    date_fin = models.DateField(db_index=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, db_index=True)
    fonctionnalites = models.JSONField(default=list)

    def __str__(self):
        return f"{self.entreprise.nom} - {self.type}"

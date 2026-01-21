from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import BaseModel, TenantModel


class Stock(TenantModel):
    produit = models.ForeignKey(
        "commerce.Produit", on_delete=models.CASCADE, related_name="stocks"
    )

    quantite = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    fournisseur = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        limit_choices_to={"type": "fournisseur"},
        db_index=True,
    )
    prix_achat = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    date_entree = models.DateField(db_index=True)

    def __str__(self):
        return f"{self.produit.nom} - {self.quantite}"

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "date_entree"]),
            models.Index(fields=["entreprise", "fournisseur"]),
        ]


class Depense(TenantModel):
    description = models.TextField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50, db_index=True)

    justificatif = models.FileField(upload_to="factures/", null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", ]),
            models.Index(fields=["entreprise", "type"]),
        ]

    def __str__(self):
        return f"{self.type} - {self.montant}"

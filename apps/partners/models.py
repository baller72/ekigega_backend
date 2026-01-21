from django.db import models

from apps.core.models import BaseModel, TenantModel


class Partner(TenantModel):
    """
    Modèle pour représenter un partenaire (client ou fournisseur).
    
    Un partenaire est une personne ou une entreprise avec laquelle
    l'utilisateur fait des affaires (ventes ou achats).
    
    Attributs:
        type (str): Type de partenaire ('client' ou 'fournisseur')
        nom (str): Nom du partenaire (max 100 caractères)
        prenom (str): Prénom du partenaire (optionnel, max 100 caractères)
        email (str): Adresse email unique par entreprise (optionnel)
        telephone (str): Numéro de téléphone (max 20 caractères)
        adresse (str): Adresse complète (optionnel)
        entreprise (ForeignKey): Entreprise propriétaire
        created_at (datetime): Horodatage de création
        updated_at (datetime): Horodatage de la dernière modification
    
    Constraints:
        - Email unique par entreprise
        - Type limité à 'client' ou 'fournisseur'
    
    Relations:
        - Les clients sont utilisés dans Vente.client
        - Les fournisseurs peuvent être utilisés dans les commandes
    
    Exemple:
        >>> client = Partner.objects.create(
        ...     entreprise=entreprise,
        ...     type='client',
        ...     nom='Dupont',
        ...     prenom='Jean',
        ...     email='jean.dupont@example.com',
        ...     telephone='+33612345678'
        ... )
        >>> print(client)
        CLIENT - Dupont
    """
    TYPE_CHOICES = (
        ("client", "Client"),
        ("fournisseur", "Fournisseur"),
    )

    entreprise = models.ForeignKey(
        "tenants.Entreprise", on_delete=models.CASCADE, related_name="partners"
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True)

    def __str__(self):
        """Retourne une représentation lisible du partenaire."""
        return f"{self.type.upper()} - {self.nom}"

    class Meta:
        unique_together = ("entreprise", "email")
        ordering = ["nom"]
        indexes = [
            models.Index(fields=["entreprise", "type"]),
            models.Index(fields=["entreprise", "nom"]),
        ]
        
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email_per_entreprise")
        ]
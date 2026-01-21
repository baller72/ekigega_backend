from rest_framework import serializers

from apps.commerce.models import Produit
from apps.partners.models import Partner

from apps.commerce.serializers import ProduitSerializer
from apps.partners.serializers import PartnerSerializer

from .models import Depense, Stock


class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = "__all__"
        read_only_fields = ("entreprise",)

    def create(self, validated_data):
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer pour les entrées de stock.
    
    Permet d'enregistrer les ajouts de stock depuis les fournisseurs.
    La quantité du produit est automatiquement incrementée via un signal Django.
    
    **Fields**:
    - `id`: UUID unique (lecture seule)
    - `produit`: UUID du produit (FK vers Produit)
    - `quantite`: Quantité ajoutée (doit être > 0)
    - `fournisseur`: UUID du fournisseur (Partner avec type="fournisseur")
    - `prix_achat`: Prix d'achat unitaire (optionnel)
    - `date_entree`: Date d'entrée du stock (indexed)
    - `entreprise`: Défini automatiquement (lecture seule)
    - `created_at`, `updated_at`: Timestamps (lecture seule)
    
    **Workflow**:
    1. Créer une instance Stock avec produit, quantite et fournisseur
    2. Le signal Django détecte la création
    3. La quantite du produit est automatiquement incrementée
    4. Un historique des entrées de stock est conservé
    
    **Exemple**:
    ```json
    POST /api/stocks/
    {
        "produit": "550e8400-e29b-41d4-a716-446655440000",
        "quantite": 100,
        "fournisseur": "650e8400-e29b-41d4-a716-446655440001",
        "prix_achat": "1.50",
        "date_entree": "2026-01-10"
    }
    ```
    
    **Réponse (201)**:
    ```json
    {
        "id": "750e8400-e29b-41d4-a716-446655440000",
        "produit": "550e8400-e29b-41d4-a716-446655440000",
        "quantite": 100,
        "fournisseur": "650e8400-e29b-41d4-a716-446655440001",
        "prix_achat": "1.50",
        "date_entree": "2026-01-10",
        "entreprise": "650e8400-e29b-41d4-a716-446655440002",
        "created_at": "2026-01-10T10:30:00Z"
    }
    ```
    """
    
    # Champs écriture (POST / PUT)
    produit = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        # source="produit",
        write_only=True
    )

    fournisseur = serializers.PrimaryKeyRelatedField(
        queryset=Partner.objects.filter(type="fournisseur"),
        # source="fournisseur",
        write_only=True
    )

    # Champs lecture (GET)
    produit_detail = ProduitSerializer(source="produit", read_only=True)
    fournisseur_detail = PartnerSerializer(source="fournisseur", read_only=True)

    class Meta:
        model = Stock
        fields = [
            "id", "quantite", "prix_achat", "date_entree",
            "entreprise", "produit", "fournisseur",
            "produit_detail", "fournisseur_detail",
            "created_at", "updated_at"
        ]
        read_only_fields = ("entreprise",)
    
    def validate_quantite(self, value):
        """Vérifie que la quantité est positive."""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être strictement positive.")
        return value
    
    def create(self, validated_data):
        """Assigne automatiquement l'entreprise lors de la création."""
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)



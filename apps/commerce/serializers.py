from decimal import Decimal

from rest_framework import serializers

from django.db import transaction

from apps.partners.serializers import PartnerSerializer

from .models import Categorie, Produit, Vente


class CategorieSerializer(serializers.ModelSerializer):
    """
    Serializer pour la gestion des catégories.

    **Validation** : Garantit l'unicité du nom par entreprise (case-insensitive).
    
    **Fields** :
    - `id` : UUID unique (lecture seule)
    - `nom` : Nom de la catégorie (unique par entreprise, max 100 caractères)
    - `entreprise` : Lien vers l'entreprise (lecture seule, défini automatiquement)
    - `created_at`, `updated_at` : Timestamps (lecture seule)
    """
    class Meta:
        model = Categorie
        fields = "__all__"
        read_only_fields = ("entreprise",)

    def validate_nom(self, value):
        request = self.context.get("request")
        entreprise = getattr(request.user, "entreprise", None) if request else None

        qs = Categorie.objects.filter(entreprise=entreprise, nom__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Une catégorie avec ce nom existe déjà pour cette entreprise."
            )
        return value

    def create(self, validated_data):
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)


class ProduitSerializer(serializers.ModelSerializer):
    """
    Serializer pour la gestion des produits.
    
    Gère la sérialisation/désérialisation des produits avec validation
    de la quantité et assignation automatique de l'entreprise.

    **Validation**:
    - quantite: Doit être >= 0
    - mesure: Doit être un code valide du CatalogueUnites
    - prix: Positif (10 chiffres, 2 décimales)

    **Fields** :
    - `id`: UUID unique (lecture seule)
    - `nom`: Nom du produit (max 150 caractères)
    - `categorie`: Catégorie du produit (max 100 caractères)
    - `prix`: Prix unitaire (Decimal 10,2)
    - `mesure`: Code unité (kg, L, m, unite, paire, piece, carton, etc.)
    - `quantite`: Quantité en stock (>= 0)
    - `entreprise`: Défini automatiquement à partir du request user (lecture seule)
    - `created_at`, `updated_at`: Timestamps (lecture seule)

    **Méthodes de conversion disponibles sur le modèle**:
    - `convert_quantity_to(qty, target_code)`: Convertir vers une autre unité
    - `convert_quantity_from(qty, source_code)`: Convertir depuis une autre unité
    
    **Exemple**:
    ```python
    serializer = ProduitSerializer(data={
        \"nom\": \"Farine de blé\",
        \"categorie\": \"Ingrédients\",
        \"prix\": \"2.50\",
        \"mesure\": \"kg\",
        \"quantite\": 100
    }, context={\"request\": request})
    if serializer.is_valid():
        produit = serializer.save()
    ```
    """
    class Meta:
        model = Produit
        fields = "__all__"
        read_only_fields = ("entreprise",)

    def validate(self, data):
        if data.get("quantite", 0) < 0:
            raise serializers.ValidationError("La quantité ne peut pas être négative.")
        return data

    def create(self, validated_data):
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)


class VenteSerializer(serializers.ModelSerializer):
    """
    Serializer pour gérer les ventes (une vente = un client + un produit).

    **Workflow** :
    1. Création : une Vente unique par combinaison (client, produit, entreprise)
    2. Gestion du stock : Produit.quantite décrémentée automatiquement
    3. Calcul du total : prix_vente = quantite * prix_unitaire (auto-calculé)
    4. Changement de statut : en attente, payée, annulée, paiement partiel, remboursée

    **Fields** :
    - `id` : UUID unique (lecture seule)
    - `client` : UUID du partenaire de type "client"
    - `produit` : UUID du produit vendu
    - `quantite` : Quantité vendue (>= 1)
    - `prix_unitaire` : Prix par unité appliqué
    - `statut` : En attente, Payée, Annulée, Paiement partiel, Remboursée
    - `prix_vente` : Total calculé (quantite * prix_unitaire, lecture seule)
    - `entreprise` : Lien vers l'entreprise (lecture seule, défini automatiquement)
    - `created_at` : Timestamp de création (lecture seule)

    **Validations** :
    - Quantité > 0
    - Prix unitaire >= 0
    - Vérification du stock disponible
    - Vérification de compatibilité tenant (produit appartient à l'entreprise)
    - Une seule vente par combinaison (client, produit, entreprise)

    **Exemple de création** :
    ```json
    {
      "client": "550e8400-e29b-41d4-a716-446655440000",
      "produit": "650e8400-e29b-41d4-a716-446655440001",
      "quantite": 5,
      "prix_unitaire": "10.50",
      "statut": "payee"
    }
    ```

    **Réponse** :
    ```json
    {
      "id": "750e8400-e29b-41d4-a716-446655440000",
      "client": "550e8400-e29b-41d4-a716-446655440000",
      "produit": "650e8400-e29b-41d4-a716-446655440001",
      "quantite": 5,
      "prix_unitaire": "10.50",
      "prix_vente": "52.50",
      "statut": "payee",
      "created_at": "2026-01-09T10:30:00Z"
    }
    ```
    """

    client = PartnerSerializer(read_only=True)
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = Vente
        fields = (
            "id",
            "client",
            "produit",
            "quantite",
            "prix_unitaire",
            "prix_vente",
            "statut",
            "created_at",
        )
        read_only_fields = ("entreprise", "prix_vente", "created_at", "id")

    def validate(self, data):
        """Valide les données de la vente."""
        if data.get("quantite", 0) <= 0:
            raise serializers.ValidationError("La quantité doit être positive.")
        
        if data.get("prix_unitaire") is not None and data["prix_unitaire"] < 0:
            raise serializers.ValidationError("Le prix unitaire ne peut pas être négatif.")
        
        return data

    def validate_produit(self, value):
        """Valide que le produit appartient à la bonne entreprise."""
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            if value.entreprise != request.user.entreprise:
                raise serializers.ValidationError("Produit invalide pour cette entreprise.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        produit = validated_data.get("produit")
        quantite = validated_data.get("quantite")

        # Vérifier le stock
        if produit.quantite < quantite:
            raise serializers.ValidationError(
                f"Produit {produit.nom} en rupture (disponible: {produit.quantite})."
            )

        with transaction.atomic():
            # Décrémenter le stock
            produit.quantite -= quantite
            produit.save()

            # Supprimer 'entreprise' de validated_data s'il existe déjà
            validated_data.pop('entreprise', None)

            # Créer la vente avec l'entreprise
            vente = Vente.objects.create(
                entreprise=request.user.entreprise,
                **validated_data
            )

        return vente




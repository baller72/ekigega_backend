from rest_framework import serializers

from .models import VideoFormation


class VideoFormationSerializer(serializers.ModelSerializer):
    """
    Serializer pour la gestion des formations vidéo.
    
    Gère la sérialisation/désérialisation complète des formations avec validation.
    
    **Fields** :
    - `id` : UUID unique (lecture seule)
    - `titre` : Titre de la formation (max 150 caractères)
    - `reference` : Identifiant unique de référence (unique, max 50 caractères)
    - `description` : Description détaillée (text long)
    - `categorie` : Finance personnelle | Gestion entreprise | Investissement | Épargne & Retraite | Cryptomonnaies
    - `niveau` : Débutant | Intermédiaire | Avancé
    - `duree` : Durée en minutes (> 0)
    - `prix` : Prix en devise locale (Decimal 10,2, >= 0)
    - `status` : Brouillon | Publiée | Archivée
    - `objectifs` : Objectifs pédagogiques (texte long, optionnel)
    - `pre_requis` : Prérequis recommandés (texte long, optionnel)
    - `cover_image` : Image de couverture (ImageField, optionnel)
    - `url` : URL de la vidéo/ressource
    - `langue` : Code langue (ex: fr, en, es)
    - `entreprise` : Lien vers l'entreprise (lecture seule)
    - `created_at` : Timestamp de création (lecture seule)
    - `updated_at` : Timestamp de modification (lecture seule)
    
    **Validations** :
    - `titre` : Non vide, max 150 caractères
    - `reference` : Unique et non vide
    - `duree` : Entier positif
    - `prix` : Décimal positif ou zéro
    
    **Exemple** :
    ```json
    {
      "titre": "Investissement pour débutants",
      "reference": "FORM-INV-001",
      "description": "Une introduction complète aux principes...",
      "categorie": "investissement",
      "niveau": "debutant",
      "duree": 120,
      "prix": "29.99",
      "status": "publiee",
      "objectifs": "- Comprendre les bases\\n- Investir en bourse",
      "pre_requis": "Aucun",
      "url": "https://video.example.com/inv-001",
      "langue": "fr"
    }
    ```
    """
    
    class Meta:
        model = VideoFormation
        fields = [
            "id",
            "titre",
            "reference",
            "description",
            "categorie",
            "niveau",
            "duree",
            "prix",
            "status",
            "objectifs",
            "pre_requis",
            "cover_image",
            "video",
            "langue",
            "entreprise",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("entreprise", "created_at", "updated_at", "id")
    
    def validate_reference(self, value):
        """Valide que la référence est unique."""
        queryset = VideoFormation.objects.filter(reference=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Une formation avec cette référence existe déjà.")
        return value
    
    def validate_duree(self, value):
        """Valide que la durée est positive."""
        if value <= 0:
            raise serializers.ValidationError("La durée doit être supérieure à 0 minutes.")
        return value
    
    def validate_prix(self, value):
        """Valide que le prix est positif ou zéro."""
        if value < 0:
            raise serializers.ValidationError("Le prix ne peut pas être négatif.")
        return value
    
    def create(self, validated_data):
        """Crée une nouvelle formation avec l'entreprise du utilisateur."""
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)

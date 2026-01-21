from django.db import models
from django.core.validators import MinValueValidator

from apps.core.models import TenantModel


class VideoFormation(TenantModel):
    """
    Modèle pour représenter une formation vidéo.
    
    Gère les informations complètes d'une formation incluant :
    - Métadonnées (titre, description, catégorie, niveau)
    - Contenu (URL vidéo, durée, langue, cover image)
    - Structure pédagogique (objectifs, prérequis)
    - Commercialisation (prix, statut)
    - Traçabilité (date de création/modification)
    
    Attributs:
        titre (str): Titre de la formation (max 150 caractères)
        reference (str): Identifiant unique de référence (max 50 caractères)
        description (str): Description détaillée de la formation (text long)
        categorie (str): Catégorie parmi les choix disponibles
        niveau (str): Niveau de difficulté (Debutant, Intermediaire, Avance)
        duree (int): Durée de la formation en minutes
        prix (Decimal): Prix de la formation (positif, 2 décimales)
        status (str): État de la formation (brouillon, publiee, archivee)
        objectifs (str): Objectifs pédagogiques (text long)
        pre_requis (str): Prérequis recommandés (text long)
        cover_image (ImageField): Image de couverture (optionnel)
        url (URLField): URL de la vidéo/ressource
        langue (str): Langue de la formation (max 20 caractères)
        entreprise (ForeignKey): Lien vers l'entreprise (tenant)
    """
    
    CATEGORIE_CHOICES = (
        ("finance_personnelle", "Finance personnelle"),
        ("gestion_entreprise", "Gestion entreprise"),
        ("investissement", "Investissement"),
        ("epargne_retraite", "Épargne & Retraite"),
        ("cryptomonnaies", "Cryptomonnaies"),
    )
    
    NIVEAU_CHOICES = (
        ("debutant", "Débutant"),
        ("intermediaire", "Intermédiaire"),
        ("avance", "Avancé"),
    )
    
    STATUS_CHOICES = (
        ("brouillon", "Brouillon"),
        ("publiee", "Publiée"),
        ("archivee", "Archivée"),
    )
    
    titre = models.CharField(max_length=150, db_index=True)
    reference = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Identifiant unique de référence (ex: FORM-001)",
        default=""
    )
    description = models.TextField(
        help_text="Description détaillée de la formation",
        default=""
    )
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIE_CHOICES,
        db_index=True,
        default="finance_personnelle"
    )
    niveau = models.CharField(
        max_length=15,
        choices=NIVEAU_CHOICES,
        default="debutant"
    )
    duree = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Durée de la formation en minutes"
    )
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Prix en devise locale"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="brouillon",
        db_index=True
    )
    objectifs = models.TextField(
        blank=True,
        help_text="Objectifs pédagogiques (séparés par des tirets ou numérotés)"
    )
    pre_requis = models.TextField(
        blank=True,
        help_text="Prérequis recommandés pour cette formation"
    )
    cover_image = models.ImageField(
        upload_to="formations/covers/",
        blank=True,
        null=True,
        help_text="Image de couverture de la formation"
    )
    video = models.FileField(upload_to="formations/videos/", blank=True, null=True, help_text="Vidéo de la formation")
    langue = models.CharField(max_length=20)
    
    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "categorie"]),
            models.Index(fields=["entreprise", "niveau"]),
            models.Index(fields=["entreprise", "status"]),
            models.Index(fields=["entreprise", "titre"]),
        ]
    
    def __str__(self):
        """Retourne une représentation lisible de la formation."""
        return f"{self.titre} ({self.get_niveau_display()})"

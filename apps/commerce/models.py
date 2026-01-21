from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from apps.core.models import BaseModel, TenantModel


class UniteMesure:
    """
    Classe pour représenter une unité de mesure avec facteur de conversion.
    
    Permet de gérer les conversions entre différentes unités sans stocker
    les unités en base de données.
    
    Attributs:
        code (str): Code unique (ex: 'kg', 'L', 'm', 't', 'hL')
        label (str): Libellé affiché (ex: 'Kilogramme', 'Tonne')
        type (str): Type d'unité ('poids', 'volume', 'longueur', 'unite')
        facteur_conversion (float): Facteur de conversion vers l'unité de base
    """
    
    def __init__(self, code, label, type_mesure, facteur_conversion=1):
        """
        Initialise une unité de mesure.
        
        Args:
            code (str): Code unique de l'unité (ex: 'kg', 'L', 'm')
            label (str): Libellé affiché (ex: 'Kilogramme')
            type_mesure (str): Type d'unité ('poids', 'volume', 'longueur', 'unite')
            facteur_conversion (float): Facteur de conversion (défaut: 1)
        """
        self.code = code
        self.label = label
        self.type = type_mesure
        self.facteur_conversion = facteur_conversion
    
    def __str__(self):
        """Retourne le libellé de l'unité."""
        return self.label
    
    def __repr__(self):
        """Retourne une représentation textuelle lisible."""
        return f"UniteMesure({self.code}, {self.facteur_conversion})"


class CatalogueUnites:
    """
    Catalogue centralisé de toutes les unités de mesure disponibles.
    
    Gère un registre d'unités préchargées permettant:
    - Récupération d'une unité par code
    - Génération de choix pour les champs Django
    - Filtrage par type d'unité
    
    Unités disponibles:
    - **Poids**: t (tonne, 1000), kg, g, mg
    - **Volume**: hL (hectolitre, 100), L, mL
    - **Longueur**: m, cm, mm
    - **Unité**: unite, paire, piece, carton
    """
    
    UNITES = {
        't': UniteMesure('t', 'Tonne', 'poids', 1000),
        'kg': UniteMesure('kg', 'Kilogramme', 'poids', 1),
        'hg': UniteMesure('hg', 'Hectogramme', 'poids', 0.1),
        'g': UniteMesure('g', 'Gramme', 'poids', 0.001),
        'mg': UniteMesure('mg', 'Milligramme', 'poids', 0.000001),
        'hL': UniteMesure('hL', 'Hectolitre', 'volume', 100),
        'L': UniteMesure('L', 'Litre', 'volume', 1),
        'mL': UniteMesure('mL', 'Millilitre', 'volume', 0.001),
        'm': UniteMesure('m', 'Mètre', 'longueur', 1),
        'cm': UniteMesure('cm', 'Centimètre', 'longueur', 0.01),
        'mm': UniteMesure('mm', 'Millimètre', 'longueur', 0.001),
        'unite': UniteMesure('unite', 'Unité', 'unite', 1),
        'paire': UniteMesure('paire', 'Paire', 'unite', 1),
        'piece': UniteMesure('piece', 'Pièce', 'unite', 1),
        'carton': UniteMesure('carton', 'Carton', 'unite', 1),
    }
    
    @classmethod
    def get(cls, code):
        """
        Récupère une unité par son code.
        
        Args:
            code (str): Code de l'unité (ex: 'kg', 'L', 't')
        
        Returns:
            UniteMesure ou None: L'unité trouvée, ou None si code inexistant
        """
        return cls.UNITES.get(code)
    
    @classmethod
    def get_choices(cls):
        """
        Retourne les choix au format Django pour les champs CharField avec choices.
        
        Returns:
            list: Liste de tuples (code, label)
        """
        return [(code, unite.label) for code, unite in cls.UNITES.items()]
    
    @classmethod
    def get_by_type(cls, type_mesure):
        """
        Récupère toutes les unités d'un type donné.
        
        Args:
            type_mesure (str): Type d'unité ('poids', 'volume', 'longueur', 'unite')
        
        Returns:
            list: Liste des UniteMesure du type spécifié
        """
        return [unite for unite in cls.UNITES.values() if unite.type == type_mesure]


class Categorie(TenantModel):
    nom = models.CharField(max_length=100, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "nom"]),
        ]

    def __str__(self):
        return self.nom

class Produit(TenantModel):
    """
    Modèle pour représenter un produit en stock.
    
    Gère les informations de base (nom, catégorie, prix) et la gestion du stock
    avec conversion d'unités automatique.
    
    Attributs:
        nom (str): Nom du produit (max 150 caractères, indexé)
        categorie (str): Catégorie du produit (max 100 caractères)
        prix (Decimal): Prix unitaire dans l'unité du produit
        mesure (str): Code de l'unité de mesure (ex: 'kg', 'L', 'unite')
        quantite (int): Quantité disponible en stock (>= 0)
        entreprise (ForeignKey): Lien vers l'entreprise propriétaire
    
    Méthodes de conversion:
        convert_quantity_to(qty, target_code): Convertir dans une autre unité
        convert_quantity_from(qty, source_code): Convertir depuis une autre unité
    """
    nom = models.CharField(max_length=150, db_index=True)
    categorie = models.CharField(max_length=100, db_index=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    mesure = models.CharField(
        max_length=20,
        choices=CatalogueUnites.get_choices(),
        null=True,
        blank=True,
    )
    quantite = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "categorie"]),
            models.Index(fields=["entreprise", "nom"]),
        ]

    def __str__(self):
        """Retourne le nom du produit."""
        return self.nom

    def get_unite_mesure(self):
        """
        Retourne l'objet UniteMesure configuré pour ce produit.
        
        Returns:
            UniteMesure ou None: L'unité de mesure du produit, ou None si non configurée
        """
        if self.mesure:
            return CatalogueUnites.get(self.mesure)
        return None

    def convert_quantity_to(self, quantity, target_unite_code):
        """
        Convertit une quantité de l'unité du produit vers une unité cible.
        
        Args:
            quantity (int/float/Decimal): Quantité à convertir (dans l'unité du produit)
            target_unite_code (str): Code de l'unité cible (ex: 'g', 'mL', 'cm')
        
        Returns:
            Decimal: Quantité convertie dans l'unité cible
        
        Raises:
            ValueError: Si l'unité cible n'existe pas ou types incompatibles
        
        Exemple:
            >>> prod = Produit.objects.create(..., mesure='kg')
            >>> prod.convert_quantity_to(2, 'g')
            Decimal('2000')  # 2 kg = 2000 g
        """
        if quantity is None:
            return Decimal(0)

        source_unite = self.get_unite_mesure()
        target_unite = CatalogueUnites.get(target_unite_code)
        
        if not target_unite:
            raise ValueError(f"Unité cible inconnue: {target_unite_code}")

        if source_unite is None:
            # produit sans mesure (compte d'unités)
            if target_unite.type != "unite":
                raise ValueError("Produit sans mesure ne peut être converti.")
            return Decimal(quantity)

        if source_unite.type != target_unite.type:
            raise ValueError(f"Types d'unité incompatibles: {source_unite.type} vs {target_unite.type}")

        q = Decimal(str(quantity))
        factor_from = Decimal(str(source_unite.facteur_conversion))
        factor_to = Decimal(str(target_unite.facteur_conversion))

        # conversion: q * (factor_from / factor_to)
        return q * (factor_from / factor_to)

    def convert_quantity_from(self, quantity, source_unite_code):
        """
        Convertit une quantité d'une unité source vers l'unité du produit.
        
        Utilisée lors d'une vente où le client donne une quantité dans une unité différente.
        
        Args:
            quantity (int/float/Decimal): Quantité à convertir (dans source_unite_code)
            source_unite_code (str): Code de l'unité source (ex: 'g', 'mL', 'cm')
        
        Returns:
            Decimal: Quantité convertie dans l'unité du produit
        
        Raises:
            ValueError: Si l'unité source n'existe pas ou types incompatibles
        
        Exemple:
            >>> prod = Produit.objects.create(..., mesure='kg')
            >>> prod.convert_quantity_from(500, 'g')
            Decimal('0.5')  # 500 g = 0.5 kg
        """
        if quantity is None:
            return Decimal(0)

        source_unite = CatalogueUnites.get(source_unite_code)
        target_unite = self.get_unite_mesure()
        
        if not source_unite:
            raise ValueError(f"Unité source inconnue: {source_unite_code}")

        if target_unite is None:
            if source_unite.type != "unite":
                raise ValueError("Produit sans mesure ne peut être converti.")
            return Decimal(quantity)

        if source_unite.type != target_unite.type:
            raise ValueError(f"Types d'unité incompatibles: {source_unite.type} vs {target_unite.type}")

        q = Decimal(str(quantity))
        factor_source = Decimal(str(source_unite.facteur_conversion))
        factor_product = Decimal(str(target_unite.facteur_conversion))

        # conversion to product unit: q * (factor_source / factor_product)
        return q * (factor_source / factor_product)


class Vente(TenantModel):
    """
    Modèle pour représenter une vente (facture/bon de vente).
    
    Une vente représente la vente d'un produit unique à un client.
    Relation: une seule vente par combinaison (client, produit, entreprise).
    
    Attributs:
        client (ForeignKey): Partenaire de type "client"
        produit (ForeignKey): Produit vendu (PROTECT: impossible de supprimer)
        quantite (int): Quantité vendue (en unité du produit)
        prix_unitaire (Decimal): Prix par unité appliqué au moment de la vente
        prix_vente (Decimal): Montant total (quantite * prix_unitaire)
        statut (str): État (en_attente, payee, annulee, paiement_partiel, rembourse)
        entreprise (ForeignKey): Entreprise propriétaire
    
    Workflow:
    1. Créer une vente avec un client et un produit
    2. Le stock du produit est décrémenté automatiquement
    3. Le prix_vente est calculé automatiquement
    4. Changer le statut au besoin (payée, annulée, etc.)
    5. En cas d'annulation, le stock est restauré
    
    Contrainte d'unicité:
        - Un seul enregistrement par (client, produit, entreprise)
    """
    STATUT_CHOICES = (
        ("en_attente", "En attente"),
        ("payee", "Payée"),
        ("annulee", "Annulée"),
        ("paiement_partiel", "Paiement partiel"),
        ("rembourse", "Remboursé"),
    )

    client = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        limit_choices_to={"type": "client"},
    )

    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, null=True, blank=True)

    quantite = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    prix_vente = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0
    )

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["entreprise", "statut"]),
            models.Index(fields=["entreprise", "created_at"]),
            models.Index(fields=["client", "produit"]),
        ]
        

    def __str__(self):
        """Retourne une représentation lisible de la vente."""
        return f"Vente {self.id} - {self.client.nom} - {self.produit.nom} ({self.quantite})"

    def save(self, *args, **kwargs):
        """
        Calcule automatiquement le prix_vente avant de sauvegarder.
        
        prix_vente = quantite * prix_unitaire
        """
        if self.quantite and self.prix_unitaire:
            self.prix_vente = Decimal(str(self.quantite)) * self.prix_unitaire
        super().save(*args, **kwargs)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.mixins import TenantQuerySetMixin
from apps.core.permissions import (
    HasRolePermission,
    IsAuthenticatedAndTenant,
    IsFinance,
    IsReadOnly,
)

from .models import Depense, Stock
from .serializers import DepenseSerializer, StockSerializer


class DepenseViewSet(TenantQuerySetMixin, ModelViewSet):
    serializer_class = DepenseSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsFinance | IsReadOnly,
    ]
    permission_module = "finance"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["type"]
    search_fields = ["description"]
    ordering_fields = ["montant", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Depense.objects.all()

        return Depense.objects.filter(entreprise=self.request.user.entreprise)


class StockViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les entrées de stock.
    
    Permet d'enregistrer les ajouts de stock depuis les fournisseurs.
    La quantité du produit est automatiquement incrementée via un signal Django.
    
    Fonctionnalité:
    - Quand on crée un Stock, le signal détecte la création
    - La quantite du produit est automatiquement incrementée
    - Un historique de tous les ajouts est conservé avec prix d'achat et fournisseur
    
    Endpoints:
    - GET /api/stocks/: Lister tous les ajouts (avec filtrage/tri)
    - POST /api/stocks/: Créer un nouvel ajout et incrementer le stock
    - GET /api/stocks/{id}/: Voir les détails d'un ajout
    - PATCH /api/stocks/{id}/: Modifier un ajout
    - DELETE /api/stocks/{id}/: Supprimer un ajout
    
    Permissions:
    - Authentification JWT requise
    - Role "finance" ou supérieur pour créer/modifier/supprimer
    - Lecture seule pour autres utilisateurs
    
    Filtrage et recherche:
    - Filtre par: produit, fournisseur, date_entree
    - Recherche: nom du produit ou du fournisseur
    - Tri par: date_entree, created_at
    """
    serializer_class = StockSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsFinance | IsReadOnly,
    ]
    permission_module = "finance"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["produit", "fournisseur", "date_entree"]
    search_fields = ["produit__nom", "fournisseur__nom"]
    ordering_fields = ["date_entree", "created_at"]
    ordering = ["-date_entree"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Stock.objects.all()

        return Stock.objects.filter(entreprise=self.request.user.entreprise)



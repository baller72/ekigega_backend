from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.mixins import TenantQuerySetMixin
from apps.core.permissions import (
    HasRolePermission,
    IsAuthenticatedAndTenant,
    IsReadOnly,
    IsSales,
)

from .models import Categorie, Produit, Vente
from .serializers import (
    CategorieSerializer,
    ProduitSerializer,
    VenteSerializer,
)


class CategorieViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les catégories de produits.
    
    ## Description
    CRUD (Créer, Lire, Mettre à jour, Supprimer) pour les catégories permettant
    de classifier les produits par domaine.
    
    ## Endpoints
    
    ### Liste et création
    - `GET /api/categories/` : Récupérer toutes les catégories avec filtres/tri/recherche
    - `POST /api/categories/` : Créer une nouvelle catégorie
    
    ### Détail et modification
    - `GET /api/categories/{id}/` : Récupérer une catégorie spécifique
    - `PUT /api/categories/{id}/` : Remplacer entièrement une catégorie
    - `PATCH /api/categories/{id}/` : Mettre à jour partiellement une catégorie
    - `DELETE /api/categories/{id}/` : Supprimer une catégorie
    
    ## Permissions
    - Authentification JWT requise
    - Accès limité aux catégories de l'entreprise de l'utilisateur
    - Administrateurs ont accès à toutes les catégories
    
    ## Filtrage et recherche
    - Filtre: `nom` (exact match)
    - Recherche: `nom` (textuelle)
    - Tri: `nom`, `created_at`
    
    ## Format des données
    
    ### Créer une catégorie
    ```json
    {
      \"nom\": \"Électronique\"
    }
    ```
    
    ### Réponse
    ```json
    {
      \"id\": \"550e8400-e29b-41d4-a716-446655440000\",
      \"nom\": \"Électronique\",
      \"entreprise\": \"650e8400-e29b-41d4-a716-446655440001\",
      \"created_at\": \"2026-01-09T10:30:00Z\",
      \"updated_at\": \"2026-01-09T10:30:00Z\"
    }
    ```
    """
    serializer_class = CategorieSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        IsAuthenticated,
    ]
    permission_module = "commerce"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["nom"]
    search_fields = ["nom"]
    ordering_fields = ["nom", "created_at"]
    ordering = ["nom"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Categorie.objects.all()
        return Categorie.objects.filter(entreprise=self.request.user.entreprise)


class ProduitViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les produits en stock.
    Gère le catalogue avec stock, prix et unités de mesure.
    Support complet de conversion d'unités pour les ventes.
    
    Permissions: JWT requise. Role "sales" pour créer/modifier.
    Filtrage par categorie/prix. Recherche sur nom.
    
    Unités supportées: poids (t=1000, kg, g, mg),
    volume (hL=100, L, mL), longueur (m, cm, mm),
    unité (unite, paire, piece, carton).
    """
    serializer_class = ProduitSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsSales | IsReadOnly,
    ]
    permission_module = "commerce"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["categorie", "prix"]
    search_fields = ["nom"]
    ordering_fields = ["prix", "nom", "created_at"]
    ordering = ["nom"]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Produit.objects.all()

        return Produit.objects.filter(entreprise=self.request.user.entreprise)

    @action(detail=False, methods=['get'], url_path='en-stock')
    def in_stock(self, request):
        """
        Récupère les produits dont la quantité en stock n'est pas nulle.
        """
        queryset = self.get_queryset().filter(quantite__gt=0)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VenteViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les ventes.

    ## Description
    Ce viewset gère le cycle de vie complet des ventes :
    - Création : une vente par combinaison (client, produit, entreprise)
    - Gestion du stock : décrément lors de la vente
    - Changement de statut : en attente, payée, annulée, etc.
    - Restauration du stock en cas d'annulation

    ## Workflow
    1. **Créer une vente** : `POST /api/ventes/`
       - Fournir `client`, `produit`, `quantite`, `prix_unitaire`, `statut`
       - Le stock du produit est décrémenté automatiquement
       - `prix_vente` (total) est calculé automatiquement

    2. **Consulter les ventes** : `GET /api/ventes/`
       - Filtres : `statut`, `client`, `produit`
       - Recherche : `client__nom`, `client__prenom`, `produit__nom`
       - Tri : `created_at`, `statut`, `prix_vente`

    3. **Modifier une vente** : `PATCH /api/ventes/{id}/`
       - Champs modifiables : `statut` (attention au stock lors du changement)
       - `prix_vente` est auto-calculé

    4. **Marquer comme payée** : `PATCH /api/ventes/{id}/mark_paid/`
       - Change le statut à "payee"

    5. **Annuler une vente** : `PATCH /api/ventes/{id}/mark_cancelled/`
       - Change le statut à "annulee"
       - Restaure automatiquement le stock du produit

    ## Permissions
    - Authentification requise (JWT)
    - Role "sales" ou supérieur pour créer/modifier
    - Lecture seule pour les autres utilisateurs

    ## Format des données

    ### Créer une vente
    ```json
    {
      "client": "550e8400-e29b-41d4-a716-446655440000",
      "produit": "650e8400-e29b-41d4-a716-446655440001",
      "quantite": 5,
      "prix_unitaire": "10.50",
      "statut": "payee"
    }
    ```

    ### Réponse
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
    serializer_class = VenteSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsSales | IsReadOnly,
    ]
    permission_module = "commerce"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["statut", "client", "produit"]
    search_fields = ["client__nom", "client__prenom", "produit__nom"]
    ordering_fields = ["created_at", "statut", "prix_vente"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Vente.objects.all()
        return Vente.objects.filter(entreprise=user.entreprise)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated, IsSales])
    def mark_paid(self, request, pk=None):
        """
        Marquer une vente comme payée.
        
        ## Endpoint
        `PATCH /api/ventes/{id}/mark_paid/`
        
        Change le statut de la vente à "payee" si elle n'est pas déjà payée.
        
        ## Réponse
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "client": "650e8400-e29b-41d4-a716-446655440001",
          "produit": "750e8400-e29b-41d4-a716-446655440002",
          "quantite": 5,
          "prix_unitaire": "10.50",
          "prix_vente": "52.50",
          "statut": "payee",
          "created_at": "2026-01-09T10:30:00Z"
        }
        ```
        
        ## Erreurs possibles
        - 400: Vente déjà payée
        - 404: Vente non trouvée
        
        Args:
            pk: UUID de la vente
        
        Returns:
            Response: Vente mise à jour avec statut "payee"
        """
        vente = self.get_object()
        if vente.statut == "payee":
            return Response({"detail": "Vente déjà payée."}, status=status.HTTP_400_BAD_REQUEST)
        vente.statut = "payee"
        vente.save()
        serializer = self.get_serializer(vente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated, IsSales])
    def mark_cancelled(self, request, pk=None):
        """
        Annuler une vente et restaurer le stock.
        
        ## Endpoint
        `PATCH /api/ventes/{id}/mark_cancelled/`
        
        Change le statut à "annulee" et restaure automatiquement la quantité
        en stock pour le produit vendu.
        
        ## Processus
        1. Vérifier que la vente n'est pas déjà annulée
        2. Ajouter la quantité vendue en stock du produit
        3. Mettre à jour le statut de la vente
        
        ## Réponse
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "client": "650e8400-e29b-41d4-a716-446655440001",
          "produit": "750e8400-e29b-41d4-a716-446655440002",
          "quantite": 5,
          "prix_unitaire": "10.50",
          "prix_vente": "52.50",
          "statut": "annulee",
          "created_at": "2026-01-09T10:30:00Z"
        }
        ```
        
        ## Erreurs possibles
        - 400: Vente déjà annulée
        - 404: Vente non trouvée
        
        Args:
            pk: UUID de la vente
        
        Returns:
            Response: Vente avec statut "annulee" et stock restauré
        """
        from django.db import transaction
        vente = self.get_object()
        
        if vente.statut == "annulee":
            return Response({"detail": "Vente déjà annulée."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Restaurer le stock
            produit = vente.produit
            produit.quantite += vente.quantite
            produit.save()
            
            # Marquer la vente comme annulée
            vente.statut = "annulee"
            vente.save()
        
        serializer = self.get_serializer(vente)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    IsFinance,
    IsReadOnly,
)

from .models import Partner
from .serializers import PartnerSerializer


class PartnerViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les partenaires (clients et fournisseurs).
    
    Endpoints:
    - GET /api/partners/ : Récupérer tous les partenaires
    - POST /api/partners/ : Créer un nouveau partenaire
    - GET /api/partners/clients/ : Récupérer uniquement les clients
    - GET /api/partners/fournisseurs/ : Récupérer uniquement les fournisseurs
    - GET /api/partners/{id}/ : Détails d'un partenaire
    - PUT /api/partners/{id}/ : Remplacer un partenaire
    - PATCH /api/partners/{id}/ : Modifier un partenaire
    - DELETE /api/partners/{id}/ : Supprimer un partenaire
    
    Permissions: Authentification JWT + Role finance pour créer/modifier
    Filtrage: nom, email, telephone - Recherche: nom, prenom, email
    """
    serializer_class = PartnerSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsFinance | IsReadOnly,
    ]
    permission_module = "partners"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["nom", "email", "telephone"]
    search_fields = ["nom", "prenom", "email"]
    ordering_fields = ["nom", "created_at"]
    ordering = ["nom"]

    def get_queryset(self):
        """Récupère les partenaires filtrés par tenant."""
        user = self.request.user
        if user.is_superuser:
            return Partner.objects.all()
        return Partner.objects.filter(entreprise=self.request.user.entreprise)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticatedAndTenant, IsAuthenticated])
    def clients(self, request):
        """
        Récupère la liste de tous les clients.
        
        GET /api/partners/clients/
        Retourne uniquement les partenaires de type "client".
        """
        queryset = self.get_queryset().filter(type="client")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticatedAndTenant, IsAuthenticated])
    def fournisseurs(self, request):
        """
        Récupère la liste de tous les fournisseurs.
        
        GET /api/partners/fournisseurs/
        Retourne uniquement les partenaires de type "fournisseur".
        """
        queryset = self.get_queryset().filter(type="fournisseur")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


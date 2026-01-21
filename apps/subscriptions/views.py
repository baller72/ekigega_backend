from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.utils import timezone

from apps.core.mixins import TenantQuerySetMixin
from apps.core.permissions import HasRolePermission, IsAdmin, IsAuthenticatedAndTenant

from .models import Abonnement
from .serializers import AbonnementSerializer


class AbonnementViewSet(TenantQuerySetMixin, ModelViewSet):
    """
    API Endpoint pour gérer les abonnements clients.

    ## Description
    Gère les souscriptions aux offres d'abonnement avec gestion automatique 
    des transitions d'état.

    ## Workflow
    1. **Créer un abonnement** : `POST /api/abonnements/`
       - Fournir `type`, `date_debut`, `date_fin`, `prix`, `status`
       - Si `status` = "active", tout abonnement actif précédent de l'entreprise est expiré

    2. **Consulter les abonnements** : `GET /api/abonnements/`
       - Filtres : `entreprise`, `type`, `status`
       - Tri : `date_debut`, `date_fin`, `prix`

    3. **Modifier un abonnement** : `PATCH /api/abonnements/{id}/`
       - Champs modifiables : `type`, `date_debut`, `date_fin`, `prix`, `status`

    ## Permissions
    - Authentification requise (JWT)
    - Accès filtré par entreprise (tenant-scoped)
    - Role "admin" requis pour créer/modifier

    ## Statuts
    - `active` : Abonnement actif
    - `expired` : Abonnement expiré

    ## Fields
    - `id` : UUID unique (lecture seule)
    - `entreprise` : Lien vers l'entreprise (lecture seule, défini automatiquement)
    - `type` : Type d'abonnement ("basic", "medium", "premium")
    - `date_debut` : Date de début (indexed)
    - `date_fin` : Date de fin (indexed)
    - `prix` : Montant de l'abonnement
    - `status` : État ("active" ou "expired")
    - `fonctionnalites` : Détails JSON des fonctionnalités incluses
    - `created_at` : Timestamp de création (lecture seule)
    """
    serializer_class = AbonnementSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        # IsAdmin,
    ]
    permission_module = "subscriptions"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["entreprise", "type", "status"]
    search_fields = []
    ordering_fields = ["date_debut", "date_fin", "prix"]
    ordering = ["-date_debut"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Abonnement.objects.all()
            if user.is_superuser
            else Abonnement.objects.filter(entreprise=user.entreprise)
        )

        entreprise_id = self.request.query_params.get("entreprise")
        if user.is_superuser and entreprise_id:
            qs = qs.filter(entreprise__id=entreprise_id)

        return qs

    def perform_create(self, serializer):
        """Expire existing active abonnement(s) for the entreprise before creating a new active one."""
        entreprise = self.request.user.entreprise
        new_status = serializer.validated_data.get("status")
        if new_status == "active":
            today = timezone.now().date()
            Abonnement.objects.filter(entreprise=entreprise, status="active").update(
                status="expired", date_fin=today
            )

        serializer.save(entreprise=entreprise)
    
    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated, IsAdmin])
    def expire(self, request, pk=None):
        """
        Expire directement un abonnement actif.
        
        Endpoint: PATCH /api/abonnements/{id}/expire/
        
        Marque un abonnement comme "expired" et definit la date de fin a aujourd'hui.
        Uniquement accessible aux administrateurs.
        
        Returns:
            Response: Abonnement expire avec status="expired" et date_fin=aujourd'hui
            
        Erreurs:
            - 400: Abonnement deja expire
            - 404: Abonnement non trouve
        """
        abonnement = self.get_object()
        
        if abonnement.status == "expired":
            return Response(
                {"detail": "Cet abonnement est deja expire."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        today = timezone.now().date()

        if abonnement.date_fin <= today:
            abonnement.status = "expired"
            abonnement.save()
            
            serializer = self.get_serializer(abonnement)
            return Response(serializer.data, status=status.HTTP_200_OK)

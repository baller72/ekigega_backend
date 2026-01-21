from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.mixins import TenantQuerySetMixin
from apps.core.permissions import HasRolePermission, IsAdmin, IsAuthenticatedAndTenant

from .models import VideoFormation
from .serializers import VideoFormationSerializer


class VideoFormationViewSet(TenantQuerySetMixin, ModelViewSet):
  """
  API Endpoint pour gérer les formations vidéo.
  
  ## Description
  CRUD (Créer, Lire, Mettre à jour, Supprimer) pour les formations vidéo
  avec support complet des catégories, niveaux et statuts.
  
  ## Endpoints
  
  ### Liste et création
  - `GET /api/formations/` : Récupérer toutes les formations avec filtres/tri/recherche
  - `POST /api/formations/` : Créer une nouvelle formation
  
  ### Détail et modification
  - `GET /api/formations/{id}/` : Récupérer une formation spécifique
  - `PUT /api/formations/{id}/` : Remplacer entièrement une formation
  - `PATCH /api/formations/{id}/` : Mettre à jour partiellement une formation
  - `DELETE /api/formations/{id}/` : Supprimer une formation
  
  ## Permissions
  - Authentification JWT requise
  - Role "admin" ou supérieur pour créer/modifier/supprimer
  - Accès limité aux formations de l'entreprise de l'utilisateur
  - Superusers ont accès à toutes les formations
  
  ## Filtrage et recherche
  - Filtres: `categorie`, `niveau`, `status`, `langue`
  - Recherche: `titre`, `description`, `reference`
  - Tri: `titre`, `prix`, `duree`, `created_at`, `status`
  
  ## Format des données
  
  ### Créer une formation
  ```json
  {
    "titre": "Investissement pour débutants",
    "reference": "FORM-INV-001",
    "description": "Une introduction complète aux principes d'investissement...",
    "categorie": "investissement",
    "niveau": "debutant",
    "duree": 120,
    "prix": "29.99",
    "status": "publiee",
    "objectifs": "- Comprendre les bases\\n- Investir en bourse\\n- Gérer le risque",
    "pre_requis": "Aucune connaissance préalable requise",
    "url": "https://video.example.com/inv-001",
    "langue": "fr"
  }
  ```
  
  ### Réponse
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "titre": "Investissement pour débutants",
    "reference": "FORM-INV-001",
    "description": "Une introduction complète...",
    "categorie": "investissement",
    "niveau": "debutant",
    "duree": 120,
    "prix": "29.99",
    "status": "publiee",
    "objectifs": "- Comprendre les bases...",
    "pre_requis": "Aucune",
    "cover_image": "https://example.com/formations/covers/inv-001.jpg",
    "url": "https://video.example.com/inv-001",
    "langue": "fr",
    "entreprise": "650e8400-e29b-41d4-a716-446655440001",
    "created_at": "2026-01-10T10:30:00Z",
    "updated_at": "2026-01-10T10:30:00Z"
  }
  ```
  """
  serializer_class = VideoFormationSerializer
  permission_classes = [
      IsAuthenticated,
      IsAuthenticatedAndTenant,
      # HasRolePermission,
      # IsAdmin,
  ]
  permission_module = "education"

  filter_backends = [
      DjangoFilterBackend,
      filters.SearchFilter,
      filters.OrderingFilter,
  ]
  filterset_fields = ["categorie", "niveau", "status", "langue"]
  search_fields = ["titre", "description", "reference"]
  ordering_fields = ["titre", "prix", "duree", "created_at", "status"]
  ordering = ["-created_at"]

  def get_queryset(self):
      user = self.request.user

      if user.is_superuser:
          return VideoFormation.objects.all()

      return VideoFormation.objects.filter(entreprise=self.request.user.entreprise)

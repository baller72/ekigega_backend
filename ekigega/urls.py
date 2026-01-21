from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from apps.ai.ml.views.analytics import ExpenseMLAnalyticsView, SalesMLAnalyticsView
from apps.ai.ml.views.health import EnterpriseHealthView
from apps.commerce.views import (
    CategorieViewSet,
    ProduitViewSet,
    VenteViewSet,
)
from apps.core.views import HealthView
from apps.education.views import VideoFormationViewSet
from apps.finance.views import DepenseViewSet, StockViewSet
from apps.logs.views import AuditLogViewSet
from apps.partners.views import PartnerViewSet
from apps.subscriptions.views import AbonnementViewSet
from apps.tenants.views import EntrepriseViewSet

router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partners")
router.register(r"tenants", EntrepriseViewSet, basename="tenants")
router.register(r"categories", CategorieViewSet, basename="categories")
router.register(r"produits", ProduitViewSet, basename="produits")
router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"ventes", VenteViewSet, basename="ventes")
router.register(r"depenses", DepenseViewSet, basename="depenses")
router.register(r"abonnements", AbonnementViewSet, basename="abonnements")
router.register(r"videos", VideoFormationViewSet, basename="videos")
router.register(r"logs", AuditLogViewSet, basename="logs")

# Définition des métadonnées pour l'API
swagger_info = openapi.Info(
    title="ekigega API",
    default_version="v1",
    description="""
    # Documentation complète de l'API Ekigega

    ## Authentification
    L'API utilise JWT (JSON Web Tokens) pour l'authentification.

    ### Obtenir un token :
    1. Utilisez l'endpoint `/api/token/` pour obtenir un token d'accès et de rafraîchissement
    2. Incluez le token dans les en-têtes : `Authorization: Bearer <votre_token>`

    ## Modifications Récentes

    ### Ventes (Commerce)
    - **Model Vente** : refactorisé pour supporter plusieurs produits par vente
    - **Workflow amélioré** : création transactionnelle avec gestion du stock
    - **Conversion d'unités** : support des conversions de mesures (kg→g, L→mL, etc.)
    - **Nouveaux endpoints** :
      - `PATCH /api/ventes/{id}/mark_paid/` — marquer comme payée
      - `PATCH /api/ventes/{id}/mark_cancelled/` — annuler et restaurer stock
      - `GET /api/ventes/{id}/items/` — récupérer les lignes de vente

    ### Gestion des Doublons (Catégories)
    - **Contrainte d'unicité** : impossible d'avoir 2 catégories au même nom par entreprise
    - **Validation API** : contrôle case-insensitive lors de la création/modification

    ### Abonnements
    - **Expiration automatique** : lors de l'ajout d'un nouvel abonnement actif, l'ancien est expiré

    ### Unités de Mesure
    - **Conversion automatique** : les quantités sont converties vers l'unité du produit
    - **Support multi-types** : poids, volume, unité générique
    - **Facteur de conversion** : configurable pour chaque unité

    ### Analytics / Dashboard
    - **KPIs enrichis** :
      - Solde de caisse (cash_in - cash_out)
      - Chiffre d'affaires (somme des prix de vente)
      - Nombre de ventes, clients, produits en stock
      - Panier moyen
      - Top 10 produits les plus vendus
    - **Caching** : résultats mis en cache pour performance

    ## Endpoints principaux

    ### Commerce (`/api/`)
    - **Catégories** : `GET/POST/PATCH /categories/` — gestion des catégories
    - **Produits** : `GET/POST/PATCH /produits/` — gestion des produits
    - **Unités** : `GET/POST /unites/` — unités de mesure (globales)
    - **Ventes** : 
      - `POST /ventes/` — créer une vente avec items
      - `GET /ventes/` — lister (filtre statut, client)
      - `PATCH /ventes/{id}/` — modifier client/statut
      - `GET /ventes/{id}/items/` — récupérer les lignes
      - `PATCH /ventes/{id}/mark_paid/` — marquer payée
      - `PATCH /ventes/{id}/mark_cancelled/` — annuler

    ### Finance (`/api/`)
    - **Stock** : `GET/POST /stocks/` — enregistrement des approvisionnements
    - **Conditionnement** : `GET/POST /conditionnements/` — variantes de vente
    - **Dépenses** : `GET/POST /depenses/` — enregistrement des dépenses

    ### Abonnements (`/api/`)
    - **Abonnements** : `GET/POST/PATCH /abonnements/` — gestion des abonnements clients

    ### Analytics (`/api/analytics/`)
    - **Dashboard** : `GET /dashboard/` — KPIs synthétiques
    - **Cashflow** : `GET /cashflow/` — entrées/sorties de trésorerie

    ## Payload Exemple : Créer une Vente

    ```json
    POST /api/ventes/
    {
      "client": "<uuid_client>",
      "statut": "payee",
      "items": [
        {
          "produit": "<uuid_produit>",
          "quantite": 5,
          "unite": "<uuid_unite (optionnel)>",
          "prix_unitaire": 10.50
        }
      ]
    }
    ```

    ## Codes de statut HTTP

    | Code | Description |
    |------|-------------|
    | 200 | Succès |
    | 201 | Créé avec succès |
    | 400 | Mauvaise requête (validation échouée) |
    | 401 | Non authentifié |
    | 403 | Permission refusée |
    | 404 | Non trouvé |
    | 409 | Conflit (ex: doublon détecté) |
    | 500 | Erreur serveur |

    ## Rate Limiting
    L'API applique des limites de requêtes par utilisateur pour assurer la stabilité du système.

    ## Environnement
    - Production : `https://api.ekigega.com`
    - Développement : `http://localhost:8000`
    """,
    terms_of_service="https://ekigega-backend.onrender.com/terms/",
    contact=openapi.Contact(
        email="support@ekigega.com",
        name="Support Ekigega",
        url="https://ekigega.com/contact",
    ),
    license=openapi.License(
        name="Proprietary License", url="https://ekigega-backend.onrender.com/license"
    ),
)

schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path("", HealthView.as_view()),
    path("admin/", admin.site.urls),
    # Documentation API
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API Endpoints
    path("api/", include(router.urls)),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/analytics/", include("apps.analytics.urls")),

    path("api/ml/analytics/expenses/", ExpenseMLAnalyticsView.as_view()),
    path("api/ml/analytics/sales/", SalesMLAnalyticsView.as_view()),
    path("api/ml/health/", EnterpriseHealthView.as_view()),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

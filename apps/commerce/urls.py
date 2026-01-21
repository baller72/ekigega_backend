from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import CategorieViewSet, ProduitViewSet, VenteViewSet

router = DefaultRouter()
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"produits", ProduitViewSet, basename="produit")
router.register(r"ventes", VenteViewSet, basename="vente")

urlpatterns = [
    path("", include(router.urls)),
]

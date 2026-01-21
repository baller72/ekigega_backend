from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services.sales import top_products_month
from apps.core.permissions import IsSales


class TopProductsMonthView(APIView):
    """
    Vue pour récupérer les produits les plus vendus du mois courant.
    
    GET /analytics/top-products-month/?limit=10
    
    Returns:
        {
            "count": int,
            "data": [
                {
                    "produit_id": int,
                    "produit_nom": str,
                    "categorie": str,
                    "quantite_vendue": int,
                    "nombre_ventes": int,
                    "prix_unitaire": float,
                    "chiffre_affaires": float
                },
                ...
            ]
        }
    """
    permission_classes = [IsAuthenticated, IsSales]

    def get(self, request):
        entreprise = request.user.entreprise
        limit = int(request.query_params.get('limit', 10))
        
        if limit < 1 or limit > 100:
            limit = 10
        
        products = top_products_month(entreprise, limit=limit)
        
        return Response({
            "count": len(products),
            "data": products
        })

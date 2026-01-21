from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services.cashflow import cashflow_comparison, cashflow_summary
from apps.analytics.services.dashboard import (
    dernieres_ventes,
    top_clients,
    total_fournisseurs,
    total_produits,
)
from apps.analytics.services.kpis import global_kpis
from apps.analytics.services.trends import monthly_sales_trend
from apps.analytics.services.sales import top_products_month
from apps.core.permissions import IsFinance, IsReadOnly, IsSales


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsFinance | IsSales | IsReadOnly]

    def get(self, request):
        entreprise = request.user.entreprise
        limit = int(request.query_params.get('top_products_limit', 10))
        top_clients_limit = int(request.query_params.get('top_clients_limit', 10))
        dernieres_ventes_limit = int(request.query_params.get('dernieres_ventes_limit', 5))
        
        if limit < 1 or limit > 100:
            limit = 10
        
        if top_clients_limit < 1 or top_clients_limit > 100:
            top_clients_limit = 10
        
        if dernieres_ventes_limit < 1 or dernieres_ventes_limit > 50:
            dernieres_ventes_limit = 5

        data = {
            # "cashflow": cashflow_summary(entreprise),
            "cashflow": cashflow_comparison(entreprise),
            "kpis": global_kpis(entreprise),
            "sales_trend": monthly_sales_trend(entreprise),
            "top_products": top_products_month(entreprise, limit=limit),
            "total_produits": total_produits(entreprise),
            "total_fournisseurs": total_fournisseurs(entreprise),
            "top_clients": top_clients(entreprise, limit=top_clients_limit),
            "dernieres_ventes": dernieres_ventes(entreprise, limit=dernieres_ventes_limit),
        }

        return Response(data)


class CashflowView(APIView):
    permission_classes = [IsAuthenticated, IsFinance | IsReadOnly]

    def get(self, request):
        entreprise = request.user.entreprise
        return Response({
            "summary": cashflow_summary(entreprise),
            "comparison": cashflow_comparison(entreprise)
        })

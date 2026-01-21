from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.commerce.models import Vente
from apps.finance.models import Depense
from apps.ai.ml.services.models import expense_ml_analysis, sales_ml_analysis

class SalesMLAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entreprise = request.user.entreprise
        ventes = Vente.objects.filter(entreprise=entreprise)

        data = sales_ml_analysis(ventes)
        return Response(data)
    
    # path("ml/analytics/sales/", SalesMLAnalyticsView.as_view())

class ExpenseMLAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entreprise = request.user.entreprise
        depenses = Depense.objects.filter(entreprise=entreprise)

        data = expense_ml_analysis(depenses)
        return Response(data)
    
    # path("ml/analytics/expenses/", ExpenseMLAnalyticsView.as_view()),
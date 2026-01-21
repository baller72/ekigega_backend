from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict

from apps.analytics.services.cache import cache_get_or_set
from apps.commerce.models import Vente
from apps.finance.models import Depense


def monthly_sales_trend(entreprise):
    """
    Calcule la tendance mensuelle incluant les revenus, les dépenses et le solde.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        list: Liste de dictionnaires {month, income, expenses, total}
    """
    key = f"monthly_trend:{entreprise.id}"

    def compute():
        # 1. Récupérer les revenus (ventes) par mois
        # On ne prend que les ventes payées ou partiellement payées pour le flux réel
        income_qs = (
            Vente.objects.filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel']
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(income=Sum("prix_vente"))
            .order_by("month")
        )

        # 2. Récupérer les dépenses par mois
        expenses_qs = (
            Depense.objects.filter(entreprise=entreprise)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(expenses=Sum("montant"))
            .order_by("month")
        )

        # 3. Fusionner les données
        trends = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})

        for item in income_qs:
            month = item["month"]
            trends[month]["income"] = float(item["income"] or 0)

        for item in expenses_qs:
            month = item["month"]
            trends[month]["expenses"] = float(item["expenses"] or 0)

        # 4. Convertir en liste ordonnée avec calcul du total (solde)
        sorted_months = sorted(trends.keys())
        results = []
        for month in sorted_months:
            income = trends[month]["income"]
            expenses = trends[month]["expenses"]
            results.append({
                "month": month,
                "income": income,
                "expenses": expenses,
                "total": income - expenses
            })

        return results

    return cache_get_or_set(key, compute)


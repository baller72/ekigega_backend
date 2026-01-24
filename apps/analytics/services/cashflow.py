from datetime import datetime
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.analytics.services.cache import cache_get_or_set
from apps.commerce.models import Vente
from apps.finance.models import Depense, Stock


def cashflow_summary(entreprise):
    """
    Calcule le résumé du cashflow global (tous les temps).
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        dict: Dictionnaire contenant cash_in, cash_out et balance globaux
    """
    key = f"cashflow:{entreprise.id}"

    def compute():
        line_total = ExpressionWrapper(
            F("prix_unitaire") * F("quantite"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        cash_in = (
            Vente.objects.filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel']
            ).aggregate(
                total=Sum(line_total)
            )["total"]
            or 0
        )

        cash_out = (
            Depense.objects.filter(entreprise=entreprise).aggregate(
                total=Sum("montant")
            )["total"]
            or 0
        )

        return {
            "cash_in": float(cash_in),
            "cash_out": float(cash_out),
            "balance": float(cash_in - cash_out),
        }

    return cache_get_or_set(key, compute)


def cashflow_current_month(entreprise):
    """
    Calcule le cashflow du mois en cours.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        dict: Dictionnaire contenant cash_in, cash_out et balance du mois courant
    """
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    key = f"cashflow_current_month:{entreprise.id}:{start_of_month.strftime('%Y-%m')}"

    def compute():
        line_total = ExpressionWrapper(
            F("prix_unitaire") * F("quantite"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        cash_in = (
            Vente.objects.filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel'],
                created_at__gte=start_of_month
            ).aggregate(total=Sum(line_total))["total"]
            or 0
        )

        cash_out = (
            Depense.objects.filter(
                entreprise=entreprise,
                created_at__gte=start_of_month
            ).aggregate(total=Sum("montant"))["total"]
            or 0
        )

        return {
            "cash_in": float(cash_in),
            "cash_out": float(cash_out),
            "balance": float(cash_in - cash_out),
        }

    return cache_get_or_set(key, compute)


def cashflow_previous_month(entreprise):
    """
    Calcule le cashflow du mois précédent.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        dict: Dictionnaire contenant cash_in, cash_out et balance du mois précédent
    """
    now = timezone.now()
    start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_previous_month = start_of_current_month - relativedelta(months=1)
    
    key = f"cashflow_previous_month:{entreprise.id}:{start_of_previous_month.strftime('%Y-%m')}"

    def compute():
        line_total = ExpressionWrapper(
            F("prix_unitaire") * F("quantite"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        # stock_total_expr = ExpressionWrapper(
        #     F("quantite") * F("prix_achat"),
        #     output_field=DecimalField(max_digits=20, decimal_places=2),
        # )

        cash_in = (
            Vente.objects.filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel'],
                created_at__gte=start_of_previous_month,
                created_at__lt=start_of_current_month
            ).aggregate(total=Sum(line_total))["total"]
            or 0
        )

        cash_out = (
            Depense.objects.filter(
                entreprise=entreprise,
                created_at__gte=start_of_previous_month,
                created_at__lt=start_of_current_month
            ).aggregate(total=Sum("montant"))["total"]
            or 0
        ) 

        return {
            "cash_in": float(cash_in),
            "cash_out": float(cash_out),
            "balance": float(cash_in - cash_out),
        }

    return cache_get_or_set(key, compute)


def cashflow_comparison(entreprise):
    """
    Compare le cashflow du mois courant avec le mois précédent.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        dict: Dictionnaire contenant les données du mois courant, du mois précédent,
              et les variations (absolues et en pourcentage)
    """
    current = cashflow_current_month(entreprise)
    previous = cashflow_previous_month(entreprise)
    
    # Calculer les variations
    def calculate_variation(current_val, previous_val):
        diff = current_val - previous_val
        if previous_val != 0:
            percentage = (diff / previous_val) * 100
        else:
            percentage = 100 if current_val > 0 else 0
        
        return {
            "absolute": round(diff, 2),
            "percentage": round(percentage, 2)
        }
    
    return {
        "current_month": current,
        "previous_month": previous,
        # "variations": {
        #     "cash_in": calculate_variation(current["cash_in"], previous["cash_in"]),
        #     "cash_out": calculate_variation(current["cash_out"], previous["cash_out"]),
        #     "balance": calculate_variation(current["balance"], previous["balance"])
        # }
    }


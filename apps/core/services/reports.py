from commerce.models import Vente
from finance.models import Depense

from django.db.models import Sum


def generate_monthly_report(entreprise, month, year):
    ventes = Vente.objects.filter(
        entreprise=entreprise, created_at__month=month, created_at__year=year
    ).aggregate(total=Sum("produit__prix"))

    depenses = Depense.objects.filter(
        entreprise=entreprise, created_at__month=month, created_at__year=year
    ).aggregate(total=Sum("montant"))

    return {
        "chiffre_affaires": ventes["total"] or 0,
        "depenses": depenses["total"] or 0,
        "resultat": (ventes["total"] or 0) - (depenses["total"] or 0),
    }

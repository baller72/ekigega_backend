from commerce.models import Vente
from finance.models import Depense

from django.db.models import Sum


def compute_kpis(entreprise):
    ventes = Vente.objects.filter(entreprise=entreprise)
    depenses = Depense.objects.filter(entreprise=entreprise)

    return {
        "total_ventes": ventes.count(),
        "revenus": ventes.aggregate(Sum("produit__prix"))["produit__prix__sum"] or 0,
        "depenses": depenses.aggregate(Sum("montant"))["montant__sum"] or 0,
    }

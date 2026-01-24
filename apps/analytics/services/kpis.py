from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from apps.analytics.services.cache import cache_get_or_set
from apps.commerce.models import Vente
from apps.finance.models import Depense, Stock
from apps.partners.models import Partner


def global_kpis(entreprise):
    key = f"kpis:{entreprise.id}"

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def compute():
        total_clients = Partner.objects.filter(
            entreprise=entreprise, type="client"
        ).count()
        total_ventes = Vente.objects.filter(entreprise=entreprise).count()

        # chiffre d'affaire: sum(prix_unitaire * quantite) from Vente
        line_total = ExpressionWrapper(
            F("prix_unitaire") * F("quantite"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        ca = (
            Vente.objects.filter(entreprise=entreprise).aggregate(
                total=Sum(line_total)
            )["total"]
            or 0
        )

        depenses = (
            Depense.objects.filter(entreprise=entreprise).aggregate(
                total=Sum("montant")
            )["total"]
            or 0
        )

        # total produits en stock
        total_stock = (
            Stock.objects.filter(entreprise=entreprise).aggregate(
                total=Sum("quantite")
            )["total"]
            or 0
        )

        total_stock_month = (
            Stock.objects.filter(entreprise=entreprise).aggregate(
                total=Sum("quantite"),
                created_at__gte=start_of_month
            )["total"]
            or 0
        )

        # panier moyen
        panier_moyen = 0
        if total_ventes:
            panier_moyen = float(ca) / float(total_ventes)

        # produits les plus vendus (top 10)
        top_products_qs = (
            Vente.objects.filter(entreprise=entreprise)
            .values("produit", "produit__nom")
            .annotate(total_qty=Sum("quantite"))
            .order_by("-total_qty")[:10]
        )
        top_products = [
            {
                "produit_id": p["produit"],
                "nom": p.get("produit__nom"),
                "quantite": p["total_qty"],
            }
            for p in top_products_qs
        ]

        return {
            "total_clients": total_clients,
            "total_ventes": total_ventes,
            "chiffre_affaire": ca,
            "depenses": depenses,
            "total_stock": total_stock,
            "total_stock_month": total_stock_month,
            "panier_moyen": panier_moyen,
            "top_products": top_products,
        }

    return cache_get_or_set(key, compute)

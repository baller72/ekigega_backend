from datetime import datetime
from django.db.models import Sum, Count
from django.utils import timezone

from apps.analytics.services.cache import cache_get_or_set, cache_delete
from apps.commerce.models import Vente


def invalidate_analytics_cache(entreprise):
    keys = [
        f"cashflow:{entreprise}",
        f"kpis:{entreprise}",
        f"monthly_trend:{entreprise}",
        f"top_products:{entreprise}",
        f"total_produits:{entreprise.id}",
        f"total_fournisseurs:{entreprise.id}",
        # Note: top_clients and dernieres_ventes have limit parameters
        # We'll invalidate common limits
        f"top_clients:{entreprise.id}:10",
        f"dernieres_ventes:{entreprise.id}:5",
    ]
    for key in keys:
        cache_delete(key)


def top_products_month(entreprise, limit=10):
    """
    Récupère les produits les plus vendus du mois courant.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
        limit: Nombre maximum de produits à retourner (défaut: 10)
    
    Returns:
        list: Liste de dictionnaires avec les infos des produits vendus
              {
                  'produit_id': int,
                  'produit_nom': str,
                  'categorie': str,
                  'quantite_vendue': int,
                  'nombre_ventes': int,
                  'prix_unitaire': Decimal,
                  'chiffre_affaires': Decimal,
              }
    """
    cache_key = f"top_products:{entreprise.id}"
    
    def calculate_top_products():
        
        # Récupérer le mois courant
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Requête pour les produits les plus vendus
        top_products = (
            Vente.objects
            .filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel'],  # Seules les ventes payées/partiellement payées
                created_at__gte=month_start
            )
            .values('produit', 'produit__nom', 'produit__categorie', 'prix_unitaire')
            .annotate(
                quantite_vendue=Sum('quantite'),
                nombre_ventes=Count('id'),
                chiffre_affaires=Sum('prix_vente')
            )
            .order_by('-quantite_vendue')
        )
        
        # Formater les résultats
        results = []
        for item in top_products:
            results.append({
                'produit_id': item['produit'],
                'produit_nom': item['produit__nom'],
                'categorie': item['produit__categorie'],
                'quantite_vendue': item['quantite_vendue'],
                'nombre_ventes': item['nombre_ventes'],
                'prix_unitaire': float(item['prix_unitaire']),
                'chiffre_affaires': float(item['chiffre_affaires']),
            })

        return results
    
    # Mettre en cache pour 1 heure
    cached_data = cache_get_or_set(cache_key, calculate_top_products)
    
    if cached_data:
        return cached_data[:limit]  
    return []

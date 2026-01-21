from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum

from apps.analytics.services.cache import cache_get_or_set
from apps.commerce.models import Produit, Vente
from apps.partners.models import Partner


def total_produits(entreprise):
    """
    Calcule le nombre total de produits pour une entreprise.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        int: Nombre total de produits
    """
    key = f"total_produits:{entreprise.id}"
    
    def compute():
        return Produit.objects.filter(entreprise=entreprise).count()
    
    return cache_get_or_set(key, compute)


def total_fournisseurs(entreprise):
    """
    Calcule le nombre total de fournisseurs pour une entreprise.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
    
    Returns:
        int: Nombre total de fournisseurs
    """
    key = f"total_fournisseurs:{entreprise.id}"
    
    def compute():
        return Partner.objects.filter(
            entreprise=entreprise, 
            type="fournisseur"
        ).count()
    
    return cache_get_or_set(key, compute)


def top_clients(entreprise, limit=10):
    """
    Récupère les meilleurs clients basés sur le total des ventes.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
        limit: Nombre maximum de clients à retourner (défaut: 10)
    
    Returns:
        list: Liste de dictionnaires avec les infos des clients
              {
                  'client_id': int,
                  'nom': str,
                  'prenom': str,
                  'total_ventes': int (nombre de ventes),
                  'somme_total': Decimal (somme du montant total)
              }
    """
    key = f"top_clients:{entreprise.id}:{limit}"
    
    def compute():
        # Calculer le total de vente pour chaque ligne
        line_total = ExpressionWrapper(
            F("prix_unitaire") * F("quantite"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )
        
        # Agréger par client
        top_clients_qs = (
            Vente.objects
            .filter(
                entreprise=entreprise,
                statut__in=['payee', 'paiement_partiel']  # Seules les ventes payées
            )
            .values('client', 'client__nom', 'client__prenom')
            .annotate(
                total_ventes=Count('id'),
                somme_total=Sum(line_total)
            )
            .order_by('-somme_total')[:limit]
        )
        
        # Formater les résultats
        results = []
        for item in top_clients_qs:
            results.append({
                'client_id': item['client'],
                'nom': item['client__nom'],
                'prenom': item['client__prenom'] or '',
                'total_ventes': item['total_ventes'],
                'somme_total': float(item['somme_total']) if item['somme_total'] else 0,
            })
        
        return results
    
    return cache_get_or_set(key, compute)


def dernieres_ventes(entreprise, limit=5):
    """
    Récupère les dernières ventes effectuées dans le système.
    
    Args:
        entreprise: Entreprise pour laquelle récupérer les données
        limit: Nombre de ventes à retourner (défaut: 5)
    
    Returns:
        list: Liste de dictionnaires avec les infos des ventes
              {
                  'vente_id': int,
                  'client_nom': str,
                  'client_prenom': str,
                  'produit_nom': str,
                  'quantite': int,
                  'prix_unitaire': float,
                  'prix_vente': float,
                  'statut': str,
                  'date_creation': str (ISO format)
              }
    """
    key = f"dernieres_ventes:{entreprise.id}:{limit}"
    
    def compute():
        ventes = (
            Vente.objects
            .filter(entreprise=entreprise)
            .select_related('client', 'produit')
            .order_by('-created_at')[:limit]
        )
        
        results = []
        for vente in ventes:
            results.append({
                'vente_id': vente.id,
                'client_nom': vente.client.nom,
                'client_prenom': vente.client.prenom or '',
                'produit_nom': vente.produit.nom if vente.produit else '',
                'quantite': vente.quantite,
                'prix_unitaire': float(vente.prix_unitaire),
                'prix_vente': float(vente.prix_vente) if vente.prix_vente else 0,
                'statut': vente.statut,
                'date_creation': vente.created_at.isoformat(),
            })
        
        return results
    
    return cache_get_or_set(key, compute)

import json

from django.conf import settings
from django.core.cache import cache


def cache_get_or_set(key, func=None, ttl=settings.ANALYTICS_CACHE_TTL):
    """
    Vérifie le cache, sinon exécute func(), stocke et renvoie le résultat.
    
    Args:
        key: Clé de cache
        func: Fonction à exécuter si pas de cache (obligatoire)
        ttl: Time To Live en secondes
    
    Returns:
        Données du cache ou résultat de func()
    
    Raises:
        ValueError: Si func=None et pas de cache
    """
    cached = cache.get(key)
    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            # Si le cache est corrompu, le supprimer
            cache.delete(key)
    
    # Si pas de cache, func est obligatoire
    if func is None:
        raise ValueError(
            f"cache_get_or_set() nécessite un argument 'func' "
            f"quand la clé '{key}' n'est pas en cache."
        )
    
    result = func()
    cache.set(key, json.dumps(result, default=str), ttl)
    return result


def cache_delete(key):
    cache.delete(key)

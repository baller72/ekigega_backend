"""
Tasks Celery pour la gestion des abonnements.

Vérifie automatiquement jour par jour l'expiration des abonnements
et les marque comme expirés si la date_fin est atteinte.
"""

from celery import shared_task

from django.db.models import Q
from django.utils import timezone

from .models import Abonnement


@shared_task(bind=True, max_retries=3)
def check_and_expire_subscriptions(self):
    """
    Vérifie quotidiennement les abonnements expirés.
    
    Marque automatiquement comme "expired" tous les abonnements dont
    la date_fin est aujourd'hui ou avant, et qui ne sont pas déjà expirés.
    
    Cette tâche est exécutée automatiquement chaque jour à minuit (00:00)
    par Celery Beat.
    
    Returns:
        dict: Informations sur les abonnements traités
            - expired_count: Nombre d'abonnements expirés
            - already_expired: Nombre d'abonnements déjà expirés
            - error: Message d'erreur si applicable
    
    Exemple de réponse:
        {
            "status": "success",
            "expired_count": 5,
            "already_expired": 2,
            "timestamp": "2026-01-10T00:00:00Z"
        }
    """
    try:
        today = timezone.now().date()
        
        # Récupérer tous les abonnements actifs qui devraient expirer aujourd'hui ou avant
        abonnements_to_expire = Abonnement.objects.filter(
            Q(status="active") & Q(date_fin__lte=today)
        )
        
        expired_count = abonnements_to_expire.count()
        
        # Marquer comme expirés
        updated = abonnements_to_expire.update(status="expired")
        
        # Récupérer le nombre d'abonnements déjà expirés
        already_expired_count = Abonnement.objects.filter(
            status="expired", date_fin__lte=today
        ).count()
        
        result = {
            "status": "success",
            "expired_count": updated,
            "already_expired": already_expired_count,
            "timestamp": timezone.now().isoformat(),
        }
        
        # Log l'action
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Abonnements: {updated} expirés automatiquement. "
            f"Total expirés: {already_expired_count}"
        )
        
        return result
        
    except Exception as exc:
        # Retry avec backoff exponentiel (5s, 25s, 125s)
        raise self.retry(exc=exc, countdown=5 ** self.request.retries)


@shared_task(bind=True)
def check_subscriptions_status(self):
    """
    Tâche auxiliaire pour vérifier le statut global des abonnements.
    
    Retourne des statistiques sur les abonnements (actifs, expirés, etc).
    Utile pour le monitoring et les dashboards.
    
    Returns:
        dict: Statistiques des abonnements
    """
    try:
        stats = {
            "total": Abonnement.objects.count(),
            "active": Abonnement.objects.filter(status="active").count(),
            "expired": Abonnement.objects.filter(status="expired").count(),
            "by_type": {
                "basic": Abonnement.objects.filter(type="basic").count(),
                "medium": Abonnement.objects.filter(type="medium").count(),
                "premium": Abonnement.objects.filter(type="premium").count(),
            },
        }
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": timezone.now().isoformat(),
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": timezone.now().isoformat(),
        }

"""
Configuration Celery pour le projet ekigega.

Configure les tâches asynchrones et le beat scheduler pour les tâches récurrentes.
"""

import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

load_dotenv()

# Définir le module de settings Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ekigega.settings')

app = Celery('ekigega')

# Charger la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découvrir les tasks depuis toutes les apps Django
app.autodiscover_tasks()

# Configuration du Celery Beat Scheduler
# Définit les tâches périodiques
app.conf.beat_schedule = {
    # Vérifie les abonnements expirés tous les jours à minuit (00:00)
    'check-expired-subscriptions': {
        'task': 'apps.subscriptions.tasks.check_and_expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Tous les jours à 00:00
        'options': {
            'expires': 3600,  # Expire après 1 heure
        }
    },
    
    # Vérifie le statut des abonnements toutes les 6 heures
    'check-subscriptions-status': {
        'task': 'apps.subscriptions.tasks.check_subscriptions_status',
        'schedule': crontab(minute=0, hour='*/6'),  # Toutes les 6 heures
        'options': {
            'expires': 600,  # Expire après 10 minutes
        }
    },
}

# Configuration additionnelle
app.conf.update(
    # Fuseau horaire
    timezone='UTC',
    
    # Activer UTC
    enable_utc=True,
    
    # Résultat backend (stocker les résultats des tâches)
    result_backend=os.getenv("CELERY_RESULT_BACKEND"),
    
    # Broker (queue des tâches)
    broker_url=os.getenv("CELERY_BROKER_URL"),

    # Sérialisation
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    
    # Timeout par défaut des tâches
    task_soft_time_limit=600,  # 10 minutes
    task_time_limit=900,  # 15 minutes
)


@app.task(bind=True)
def debug_task(self):
    """Tâche de test pour vérifier que Celery fonctionne."""
    print(f'Request: {self.request!r}')

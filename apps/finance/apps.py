from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.finance"

    def ready(self):
        """Importe les signaux Django au démarrage de l'app."""
        from . import signals

from django.apps import AppConfig


class CommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.commerce"

    def ready(self):
        """Importe les signaux Django au démarrage de l'app."""
        # from . import signals
        pass 

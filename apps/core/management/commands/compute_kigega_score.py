from core.models import Entreprise
from services.kpis import compute_kpis
from services.scoring import compute_kigega_score

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Calcule le score Kigega™"

    def handle(self, *args, **options):
        for entreprise in Entreprise.objects.all():
            kpis = compute_kpis(entreprise)
            score = compute_kigega_score(kpis)

            self.stdout.write(
                self.style.SUCCESS(f"{entreprise.nom} → Score Kigega™ : {score}/100")
            )

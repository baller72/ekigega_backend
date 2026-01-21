from core.models import Entreprise
from services.kpis import compute_kpis

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Calcule les KPIs financiers"

    def handle(self, *args, **options):
        for entreprise in Entreprise.objects.all():
            kpis = compute_kpis(entreprise)
            self.stdout.write(self.style.SUCCESS(f"KPIs {entreprise.nom}: {kpis}"))

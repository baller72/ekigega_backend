from datetime import date

from core.models import Entreprise
from services.reports import generate_monthly_report

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Génère les rapports financiers mensuels"

    def handle(self, *args, **options):
        today = date.today()

        for entreprise in Entreprise.objects.all():
            report = generate_monthly_report(
                entreprise=entreprise, month=today.month, year=today.year
            )
            self.stdout.write(
                self.style.SUCCESS(f"Rapport généré pour {entreprise.nom}: {report}")
            )

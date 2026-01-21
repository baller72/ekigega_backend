"""
Commande management pour tester la vérification de l'expiration des abonnements.

Usage:
    python manage.py check_expired_subscriptions
    python manage.py check_expired_subscriptions --dry-run
    python manage.py check_expired_subscriptions --verbose
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.subscriptions.models import Abonnement


class Command(BaseCommand):
    help = "Vérifier et expirer automatiquement les abonnements dont la date_fin est atteinte"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait fait sans modifier la base de données'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Afficher des détails supplémentaires sur chaque abonnement'
        )

    def handle(self, *args, **options):
        """Exécute la vérification des abonnements expirés."""
        
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        today = timezone.now().date()
        
        self.stdout.write(
            self.style.SUCCESS(f"\n{'='*60}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Vérification de l'expiration des abonnements")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Date du jour: {today}")
        )
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"MODE: DRY-RUN (Aucune modification)")
            )
        self.stdout.write(
            self.style.SUCCESS(f"{'='*60}\n")
        )
        
        # Récupérer les abonnements à expirer
        abonnements_to_expire = Abonnement.objects.filter(
            Q(status="active") & Q(date_fin__lte=today)
        )
        
        count = abonnements_to_expire.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("✓ Aucun abonnement à expirer.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ {count} abonnement(s) à expirer:"
                )
            )
            self.stdout.write("")
            
            for i, abonnement in enumerate(abonnements_to_expire, 1):
                status_color = self.style.ERROR if verbose else self.style.WARNING
                
                output = (
                    f"  {i}. ID: {abonnement.id}\n"
                    f"     Entreprise: {abonnement.entreprise.nom}\n"
                    f"     Type: {abonnement.type}\n"
                    f"     Date fin: {abonnement.date_fin}\n"
                    f"     Statut: {abonnement.status} → expired"
                )
                self.stdout.write(status_color(output))
                self.stdout.write("")
            
            if not dry_run:
                # Appliquer les changements
                updated = abonnements_to_expire.update(status="expired")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ {updated} abonnement(s) marqué(s) comme expirés.\n"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n[DRY-RUN] {count} abonnement(s) SERAIENT marqués comme expirés.\n"
                    )
                )
        
        # Afficher les statistiques
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(self.style.SUCCESS("STATISTIQUES"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))
        
        total = Abonnement.objects.count()
        active = Abonnement.objects.filter(status="active").count()
        expired = Abonnement.objects.filter(status="expired").count()
        
        self.stdout.write(
            f"Total abonnements: {self.style.WARNING(str(total))}"
        )
        self.stdout.write(
            f"Actifs: {self.style.SUCCESS(str(active))}"
        )
        self.stdout.write(
            f"Expirés: {self.style.ERROR(str(expired))}"
        )
        
        # Détails par type si verbose
        if verbose:
            self.stdout.write("\nDétails par type:")
            for type_name, type_label in Abonnement.TYPES:
                count_type = Abonnement.objects.filter(type=type_name).count()
                self.stdout.write(f"  {type_label}: {count_type}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\n{'='*60}\n")
        )
        
        self.stdout.write(
            self.style.SUCCESS("✓ Vérification terminée avec succès.")
        )

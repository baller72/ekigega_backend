import random

from faker import Faker

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Role
from apps.commerce.models import Produit, Vente
from apps.core.constants import UserRole
from apps.finance.models import Depense
from apps.partners.models import Partner
from apps.tenants.models import Entreprise

# import os
# import django

# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "ekigega.settings"  # ⚠️ nom exact de ton projet
# )

# django.setup()


fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = "Seed data for e-Kigega (production-like)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        entreprise = Entreprise.objects.create(
            nom="Entreprise Test eKigega",
            secteur="Commerce",
            type="PME",
            adresse=fake.address(),
            taille=25,
        )

        # ROLES SYSTEME
        roles_map = {}

        roles_data = {
            UserRole.ADMIN: {
                "permissions": {
                    "tenants": ["create", "read", "update"],
                    "commerce": ["create", "read", "update"],
                    "analytics": ["read"],
                }
            },
            UserRole.COMPTABLE: {
                "permissions": {
                    "finance": ["create", "read"],
                    "analytics": ["read"],
                }
            },
            UserRole.VENTES: {
                "permissions": {
                    "commerce": ["create", "read"],
                }
            },
        }

        for role_name, data in roles_data.items():
            role, _ = Role.objects.get_or_create(
                nom=role_name,
                defaults={
                    "permissions": data["permissions"],
                    # "is_system": True
                },
            )
            roles_map[role_name] = role

        # USERS (6 rôles)
        users = []

        for role_name in [
            UserRole.ADMIN,
            UserRole.COMPTABLE,
            UserRole.VENTES,
        ]:
            user = User.objects.create_user(
                email=f"{role_name.lower()}@ekigega_test.bi",
                password="test1234",
                nom=fake.last_name(),
                prenom=fake.first_name(),
                role=roles_map[role_name],
                entreprise=entreprise,
            )
            users.append(user)

        # CLIENTS (10)
        clients = []
        for _ in range(10):
            clients.append(
                Partner.objects.create(
                    entreprise=entreprise,
                    nom=fake.last_name(),
                    prenom=fake.first_name(),
                    telephone=fake.phone_number(),
                    email=fake.email(),
                    adresse=fake.address(),
                    type="client",
                )
            )

        # PRODUITS (10)
        produits = []
        for i in range(10):
            produits.append(
                Produit.objects.create(
                    entreprise=entreprise,
                    nom=f"Produit {i+1}",
                    categorie="Général",
                    prix=random.randint(5000, 50000),
                    quantite=random.randint(10, 100),
                )
            )

        # FOURNISSEURS (10)
        fournisseurs = []
        for _ in range(10):
            fournisseurs.append(
                Partner.objects.create(
                    entreprise=entreprise,
                    nom=fake.last_name(),
                    prenom=fake.first_name(),
                    email=fake.company_email(),
                    telephone=fake.phone_number(),
                    adresse=fake.address(),
                    type="fournisseur",
                )
            )

        # DÉPENSES (10)
        for _ in range(10):
            Depense.objects.create(
                entreprise=entreprise,
                categorie="Frais généraux",
                description=fake.sentence(),
                montant=random.randint(10000, 200000),
                type="CASH",
            )

        # VENTES (10)
        for _ in range(10):
            Vente.objects.create(
                entreprise=entreprise,
                client=random.choice(clients),
                produit=random.choice(produits),
                quantite=random.randint(1, 5),
                statut="PAYE",
            )

        self.stdout.write(self.style.SUCCESS("Seed terminé avec succès."))

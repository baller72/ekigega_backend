import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("partners", "0001_initial"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Produit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("nom", models.CharField(db_index=True, max_length=150)),
                ("categorie", models.CharField(db_index=True, max_length=100)),
                ("prix", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "quantite",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "entreprise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="produits",
                        to="tenants.entreprise",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Vente",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("quantite", models.IntegerField()),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("en_attente", "En attente"),
                            ("payee", "Payée"),
                            ("annulee", "Annulée"),
                            ("paiement_partiel", "Paiement partiel"),
                            ("rembourse", "Remboursé"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        limit_choices_to={"type": "client"},
                        on_delete=django.db.models.deletion.PROTECT,
                        to="partners.partner",
                    ),
                ),
                (
                    "entreprise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ventes",
                        to="tenants.entreprise",
                    ),
                ),
                (
                    "produit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="commerce.produit",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VenteProduit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("quantite", models.IntegerField()),
                ("prix_unitaire", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "entreprise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="tenants.entreprise",
                    ),
                ),
                (
                    "produit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="commerce.produit",
                    ),
                ),
                (
                    "vente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="commerce.vente",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="produit",
            index=models.Index(
                fields=["entreprise", "categorie"],
                name="commerce_pr_entrepr_d372a0_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="produit",
            index=models.Index(
                fields=["entreprise", "nom"], name="commerce_pr_entrepr_d0b989_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="vente",
            index=models.Index(
                fields=["entreprise", "statut"], name="commerce_ve_entrepr_38965f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="vente",
            index=models.Index(
                fields=["entreprise", "created_at"],
                name="commerce_ve_entrepr_13ebcd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="venteproduit",
            index=models.Index(
                fields=["entreprise", "created_at"],
                name="commerce_ve_entrepr_86b7bc_idx",
            ),
        ),
    ]

"""
Migration pour refactoriser Vente.
Supprime quantite et produit de Vente (maintenant gérés par VenteProduit).
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0006_alter_produit_mesure_alter_produit_quantite"),
    ]

    operations = [
        # Supprimer les champs quantite et produit de Vente
        # (ils sont maintenant sur VenteProduit)
        migrations.RemoveField(
            model_name="vente",
            name="quantite",
        ),
        migrations.RemoveField(
            model_name="vente",
            name="produit",
        ),
        # Ajouter prix_vente s'il n'existe pas
        # (il devrait déjà exister de la migration 0003)
    ]

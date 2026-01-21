from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Vente


@receiver(post_save, sender=Vente)
def update_stock(sender, instance, created, **kwargs):
    """
    Met à jour le stock lorsqu'une `Vente` est créée ou que son statut change.

    Changement principal suite au refactor : une `Vente` correspond désormais
    à la vente d'un seul produit. On décrémente/restaure donc la quantité
    sur `instance.produit` en fonction du statut et de la création.
    """

    # Lors de la création d'une vente, décrémente la quantité du produit vendu
    if created:
        produit = getattr(instance, "produit", None)
        if produit and getattr(instance, "quantite", None) is not None:
            produit.quantite -= instance.quantite
            produit.save()
        return

    # Lors d'une mise à jour, si le statut a changé et devient 'annulee',
    # restaurer la quantité vendue au produit.
    if kwargs.get("update_fields") and "statut" in kwargs["update_fields"]:
        if instance.statut == "annulee":
            produit = getattr(instance, "produit", None)
            if produit and getattr(instance, "quantite", None) is not None:
                produit.quantite += instance.quantite
                produit.save()
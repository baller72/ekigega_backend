"""
Signaux Django pour l'app finance.

Gère les actions automatiques lors de la création/modification des modèles.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Stock


@receiver(post_save, sender=Stock)
def increment_product_quantity(sender, instance, created, **kwargs):
    """
    Signal pour incrémenter la quantité du produit lors d'une entrée de stock.
    
    Déclenché automatiquement après la création d'une instance Stock.
    Met à jour la quantite du Produit en ajoutant la quantité spécifiée.
    
    Args:
        sender: Classe Stock
        instance: Instance Stock créée
        created: Boolean indiquant si c'est une création (True) ou modification (False)
        **kwargs: Arguments additionnels du signal
    
    Comportement:
    - Vérifie que c'est une création (created=True)
    - Récupère le produit associé
    - Ajoute la quantité du stock à la quantité du produit
    - Sauvegarde le produit avec update_fields pour optimiser
    """
    if created:
        produit = instance.produit
        produit.quantite += instance.quantite
        produit.save(update_fields=['quantite'])

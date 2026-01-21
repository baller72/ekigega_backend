from django.db import models

from apps.core.models import BaseModel


class Entreprise(BaseModel):
    nom = models.CharField(max_length=150)
    secteur = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    adresse = models.TextField()
    taille = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nom

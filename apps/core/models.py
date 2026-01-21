import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantModel(BaseModel):
    entreprise = models.ForeignKey(
        "tenants.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["entreprise", "created_at"])]

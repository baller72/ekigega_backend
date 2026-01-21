from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.logs.models import AuditLog


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ == "AuditLog":
        return

    if getattr(instance, "_skip_audit_log", False):
        return

    if not hasattr(instance, "entreprise") or instance.entreprise is None:
        return

    AuditLog.objects.create(
        entreprise=instance.entreprise,
        action=f"{sender.__name__} {'CREATED' if created else 'UPDATED'}",
        status_code=f"{201 if created else 200}",
        # details=str(instance),
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ == "AuditLog":
        return

    if hasattr(instance, "entreprise"):
        AuditLog.objects.create(
            entreprise=instance.entreprise,
            action=f"{sender.__name__} DELETED",
            status_code=200,
            # details=str(instance),
        )

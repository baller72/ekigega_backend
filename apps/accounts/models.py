import hashlib
import secrets

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from apps.core.constants import UserRole
from apps.core.models import BaseModel
from apps.tenants.models import Entreprise

from .managers import UserManager


class Role(BaseModel):
    nom = models.CharField(
        max_length=50, choices=UserRole.CHOICES, default=UserRole.VENTES
    )
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict)

    def __str__(self):
        return self.nom


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    telephone = models.CharField(max_length=20, db_index=True)

    profile = models.FileField(upload_to="profiles/", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[("actif", "Actif"), ("inactif", "Inactif")],
        default="actif",
        db_index=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        unique_together = ("email", "entreprise")

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class PasswordResetToken(BaseModel):
    """
    Modele pour stocker les tokens de reset de mot de passe.
    Utilise des tokens securises avec expiration.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_token"
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Reset Token"
        verbose_name_plural = "Reset Tokens"

    def __str__(self):
        return f"Reset token for {self.user.email}"

    @staticmethod
    def generate_token():
        """Genere un token securise."""
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Verifie si le token est valide et non expire."""
        return not self.is_used and timezone.now() < self.expires_at

    @staticmethod
    def create_for_user(user, expiry_hours=24):
        """
        Cree ou met a jour un token de reset pour un utilisateur.
        
        Args:
            user: Utilisateur pour lequel creer le token
            expiry_hours: Nombre d'heures avant expiration (defaut: 24)
        
        Returns:
            Token cree ou mis a jour
        """
        token = PasswordResetToken.generate_token()
        expires_at = timezone.now() + timezone.timedelta(hours=expiry_hours)
        
        # Supprimer ancien token s'il existe
        PasswordResetToken.objects.filter(user=user).delete()
        
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return reset_token


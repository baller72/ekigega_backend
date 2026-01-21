from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

from apps.core.constants import UserRole
from apps.tenants.serializers import EntrepriseSerializer

from .models import PasswordResetToken, Role, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    entreprise = EntrepriseSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ("password",)


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.nom", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "nom",
            "prenom",
            "email",
            "telephone",
            "profile",
            "role",
            "status",
            "created_at",
            "updated_at",
        )


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "nom",
            "prenom",
            "email",
            "telephone",
            "profile",
            "role",
            "status",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.entreprise = self.context["request"].user.entreprise
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user.status == "inactif":
            raise serializers.ValidationError({"status": "Utilisateur inactif"})

        if not user.is_active:
            raise serializers.ValidationError({"is_active": "Compte inactif"})

        if not user.is_superuser and not user.entreprise:
            raise serializers.ValidatinError({"entreprise": "Entreprise obligatoire"})

        data["user"] = UserSerializer(user).data

        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[
            validate_password,
            # RegexValidator(
            #     regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            #     message="Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre et un caractère spécial"
            # )
        ],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[
            validate_password,
            # RegexValidator(
            #     regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            #     message="Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre et un caractère spécial"
            # )
        ],
    )

    class Meta:
        model = User
        fields = ("email", "nom", "prenom", "telephone", "password", "profile", "password2", "role", "entreprise")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )

        # Pour les rôles métier, entreprise obligatoire
        if attrs.get("role") != UserRole.SUPER_ADMIN and not attrs.get("entreprise"):
            raise serializers.ValidationError(
                {"entreprise": "Entreprise obligatoire pour ce rôle."}
            )

        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer pour demander un reset de mot de passe par email."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Aucun utilisateur trouvé avec cet email ."
            )
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        reset_token = PasswordResetToken.create_for_user(user)
        return reset_token


class ValidateResetTokenSerializer(serializers.Serializer):
    """Serializer pour valider un token de reset."""
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token invalide.")
        
        if not reset_token.is_valid():
            raise serializers.ValidationError(
                "Token expiré ou déjà utilisé."
            )
        
        return value

    def get_token_object(self):
        """Recupere l'objet token valide."""
        token = self.validated_data["token"]
        return PasswordResetToken.objects.get(token=token)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer pour reset le mot de passe avec un token."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token invalide.")
        
        if not reset_token.is_valid():
            raise serializers.ValidationError(
                "Token expire ou deja utilise."
            )
        
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Les mots de passe ne correspondent pas."}
            )

        try:
            validate_password(attrs["new_password"])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def save(self):
        token_str = self.validated_data["token"]
        new_password = self.validated_data["new_password"]
        
        reset_token = PasswordResetToken.objects.get(token=token_str)
        user = reset_token.user
        
        user.set_password(new_password)
        user.save()
        
        reset_token.is_used = True
        reset_token.save()
        
        return user


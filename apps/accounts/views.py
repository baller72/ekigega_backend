from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.core.permissions import IsAdmin
from apps.core.constants import UserRole

from .models import PasswordResetToken, Role
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordSerializer,
    RoleSerializer,
    UserProfileSerializer,
    UserSerializer,
    ValidateResetTokenSerializer,
)

User = get_user_model()


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Générer le JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return User.objects.all()

        return User.objects.filter(entreprise=self.request.user.entreprise)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Vérifier que l'utilisateur n'essaie pas de se supprimer
        if instance.id == request.user.id:
            return Response(
                {"detail": "Vous ne pouvez pas supprimer votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que l'utilisateur n'essaie pas de supprimer un admin s'il n'est pas super admin
        if instance.role and instance.role.nom == UserRole.ADMIN and not request.user.is_superuser:
            return Response(
                {"detail": "Seul un super administrateur peut supprimer un administrateur."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class RequestPasswordResetView(generics.CreateAPIView):
    """
    Demander un reset de mot de passe.
    Envoie un email avec un lien de reset contenant un token securise.
    """
    serializer_class = RequestPasswordResetSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_token = serializer.save()
        
        # Envoyer l'email
        self.send_reset_email(reset_token)
        
        return Response(
            {
                "message": "Email de reset envoye. Verifie ta boite de reception.",
                "email": request.data.get("email")
            },
            status=status.HTTP_200_OK
        )

    def send_reset_email(self, reset_token):
        """
        Envoie un email de reset de mot de passe.
        Utilise un template HTML et envoie une version texte aussi.
        """
        user = reset_token.user
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"
        
        context = {
            "user": user,
            "reset_link": reset_link,
            "expiry_hours": 24,
        }
        
        # Generer le contenu HTML et texte
        html_message = render_to_string("reset_password_email.html", context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="Reinitialiser votre mot de passe",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class ValidateResetTokenView(APIView):
    """Valider qu'un token de reset est valide."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ValidateResetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            {"valid": True, "message": "Token valide"},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.CreateAPIView):
    """
    Reset le mot de passe en utilisant un token valide.
    Marque le token comme utilise apres le reset.
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                "message": "Mot de passe reinitialise avec succes",
                "email": user.email
            },
            status=status.HTTP_200_OK
        )


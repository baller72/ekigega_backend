from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from .views import (
    LoginView,
    MeAPIView,
    RegisterView,
    RequestPasswordResetView,
    ResetPasswordView,
    RoleViewSet,
    UserViewSet,
    ValidateResetTokenView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"roles", RoleViewSet, basename="roles")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("me/", MeAPIView.as_view(), name="user_profile"),
    path("request-password-reset/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    path("validate-reset-token/", ValidateResetTokenView.as_view(), name="validate_reset_token"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
] + router.urls


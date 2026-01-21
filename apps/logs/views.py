from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.core.mixins import TenantQuerySetMixin
from apps.core.permissions import HasRolePermission, IsAdmin, IsAuthenticatedAndTenant

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(TenantQuerySetMixin, ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [
        IsAuthenticatedAndTenant,
        HasRolePermission,
        IsAuthenticated,
        IsAdmin,
    ]
    permission_module = "logs"

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return AuditLog.objects.all()

        return AuditLog.objects.filter(entreprise=self.request.user.entreprise)

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise, user=self.request.user)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["action", "ip_address", "user"]
    search_fields = ["details"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]

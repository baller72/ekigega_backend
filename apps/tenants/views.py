from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import HasRolePermission, IsAdmin, IsCompanyAdmin

from .models import Entreprise
from .serializers import EntrepriseSerializer


class EntrepriseViewSet(ModelViewSet):
    serializer_class = EntrepriseSerializer
    permission_classes = [
        IsAdmin,
        IsAuthenticated,
        # IsCompanyAdmin,
        # HasRolePermission
    ]
    permission_module = "tenants"

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Entreprise.objects.all()

        return Entreprise.objects.filter(id=self.request.user.entreprise_id)

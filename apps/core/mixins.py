class TenantQuerySetMixin:
    """
    Force le filtrage par entreprise (tenant)
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(entreprise=self.request.user.entreprise)

    def perform_create(self, serializer):
        serializer.save(entreprise=self.request.user.entreprise)

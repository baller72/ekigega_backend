class TenantAdminMixin:
    """
    Sécurise l'admin Django en multi-tenant
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(entreprise=request.user.entreprise)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.entreprise = request.user.entreprise
        super().save_model(request, obj, form, change)

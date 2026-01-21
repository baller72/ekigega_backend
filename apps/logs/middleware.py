from apps.logs.models import AuditLog


class AuditLogMiddleware:
    """
    Middleware d'audit global
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        entreprise = (
            getattr(user, "entreprise", None)
            if user and user.is_authenticated
            else None
        )

        if not request.user.is_authenticated:
            return response

        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return response

        try:
            entreprise = request.user.entreprise
        except AttributeError:
            return response

        AuditLog.objects.create(
            entreprise=entreprise,
            user=request.user,
            action=self._resolve_action(request),
            method=request.method,
            path=request.path,
            object_type=self._get_object_type(request),
            object_id=self._get_object_id(request),
            ip_address=self._get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            status_code=response.status_code,
        )

        return response

    def _resolve_action(self, request):
        return f"{request.method}_{request.path.split('/')[-2].upper()}"

    def _get_ip(self, request):
        return request.META.get("REMOTE_ADDR")

    def _get_object_type(self, request):
        return request.resolver_match.app_name if request.resolver_match else ""

    def _get_object_id(self, request):
        return request.resolver_match.kwargs.get("pk", "")

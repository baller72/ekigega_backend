from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.core.constants import CRUD_ACTIONS, ROLE_PERMISSIONS, UserRole


class IsAuthenticatedAndTenant(BasePermission):
    """
    Vérifie :
    - utilisateur authentifié
    - utilisateur actif
    - utilisateur rattaché à une entreprise
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.status == "actif"
            and user.entreprise_id
        )


class HasRolePermission(BasePermission):
    """
    Permissions CRUD basées sur le rôle entreprise
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.entreprise or not user.role:
            return False
        # print(user.role.nom)
        module = getattr(view, "permission_module", None)
        if not module:
            return False
        # print(module)
        action = getattr(view, "action", None)
        if not action:
            return False
        # print(action)
        crud_action = CRUD_ACTIONS.get(action)
        if not crud_action:
            return False
        # print(crud_action)
        permissions = ROLE_PERMISSIONS.get(user.role.nom, {})
        allowed = permissions.get(module, [])
        # print(permissions)
        return crud_action in allowed


class IsRoleAllowed(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs avec un rôle autorisé.
    """

    def has_permission(self, request, view):
        allowed_roles = getattr(view, "allowed_roles", [])
        user_role = getattr(request.user, "role", None)
        if not request.user.is_authenticated:
            return False
        # Superuser peut toujours accéder
        if request.user.is_superuser:
            return True
        return user_role in allowed_roles


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and user.role.nom in (
            UserRole.ADMIN,
            # UserRole.SUPER_ADMIN
        )


class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.entreprise is not None
            and user.role.nom in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.nom in [UserRole.ADMIN, UserRole.SUPER_ADMIN]


class IsFinance(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.nom in [UserRole.ADMIN, UserRole.COMPTABLE]


class IsSales(BasePermission):
    def has_permission(self, request, view):
        return request.user.role.nom in [UserRole.ADMIN, UserRole.VENTES]


class IsSameEntreprise(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.entreprise_id == request.user.entreprise_id

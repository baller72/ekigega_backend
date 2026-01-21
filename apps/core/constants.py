CRUD_ACTIONS = {
    "list": "view",
    "retrieve": "view",
    "create": "create",
    "update": "update",
    "partial_update": "update",
    "destroy": "delete",
}


class UserRole:
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    COMPTABLE = "COMPTABLE"
    VENTES = "VENTES"
    # OPERATOR = "OPERATOR"
    # VIEWER = "VIEWER"

    CHOICES = [
        (SUPER_ADMIN, "Super_Admin"),
        (ADMIN, "Administrateur"),
        (COMPTABLE, "Comptable"),
        (VENTES, "Ventes"),
        # (OPERATOR, "Opérateur"),
        # (VIEWER, "Lecteur"),
    ]


ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: {
        "logs": ["create", "view", "update", "delete"],
        "tenants": ["create", "view", "update", "delete"],
        "partners": ["create", "view", "update", "delete"],
        "commerce": ["create", "view", "update", "delete"],
        "finance": ["create", "view", "update", "delete"],
        "subscriptions": ["create", "view", "update", "delete"],
        "education": ["create", "view", "update", "delete"],
    },
    UserRole.ADMIN: {
        "logs": ["create", "view", "update", "delete"],
        "tenants": ["create", "view", "update", "delete"],
        "partners": ["create", "view", "update", "delete"],
        "commerce": ["create", "view", "update", "delete"],
        "finance": ["create", "view", "update", "delete"],
        "subscriptions": ["create", "view", "update", "delete"],
        "education": ["create", "view", "update", "delete"],
    },
    UserRole.COMPTABLE: {
        "logs": ["create", "view", "update", "delete"],
        "tenants": ["create", "view", "update", "delete"],
        "partners": ["create", "view", "update", "delete"],
        "commerce": ["create", "view", "update", "delete"],
        "finance": ["create", "view", "update", "delete"],
        "subscriptions": ["create", "view", "update", "delete"],
        "education": ["create", "view", "update", "delete"],
    },
    UserRole.VENTES: {
        "logs": ["create", "view", "update", "delete"],
        "tenants": ["create", "view", "update", "delete"],
        "partners": ["create", "view", "update", "delete"],
        "commerce": ["create", "view", "update", "delete"],
        "finance": ["create", "view", "update", "delete"],
        "subscriptions": ["create", "view", "update", "delete"],
        "education": ["create", "view", "update", "delete"],
    },
}

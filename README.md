# Ekigega Backend – Documentation Projet

# 1. Vue d’ensemble

Ekigega Backend est une API *Django + Django REST Framework* orientée SaaS multi-tenant, où l’Entreprise (tenant) est au centre de toutes les données. Chaque requête métier est isolée par entreprise via un champ entreprise_id.

Le projet est conçu pour :
- Une utilisation production-ready
- Une gestion fine des rôles et permissions
- Des analytics financières performantes
- Une auditabilité complète des actions

# 2. Architecture générale

ekigega_backend/
│
├── apps/
│   ├── core/           # User, roles, permissions, auth
│   ├── tenants/        # Entreprises (tenants)
│   ├── products/       # Produits
│   ├── sales/          # Ventes
│   ├── expenses/       # Dépenses
│   ├── partners/       # Clients & Fournisseurs
│   ├── subscriptions/  # Abonnements
│   ├── education/         # Formations vidéos
│   ├── analytics/      # Tableaux de bord & KPI
│   ├── logs/           # Audit logs
│
├── ekigega/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py

# 3. Multi-tenancy

Entreprise = tenant
Tous les modèles métiers héritent implicitement de :
entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
Isolation stricte des données par entreprise
Les superusers peuvent contourner la contrainte entreprise

# 4. Authentification & Sécurité

JWT (SimpleJWT)
Endpoints sécurisés par *IsAuthenticated*
Endpoints auth :
Méthode	Endpoint	                Description
POST	/api/auth/login/	        Login utilisateur
POST	/api/auth/register/	        Inscription contrôlée
GET	    /api/auth/me/	            Profil utilisateur connecté
POST	/api/auth/token/refresh/	Rafraîchir le token

# 5. Utilisateurs, Rôles & Permissions

## 5.1 Modèle User

Champs principaux :
- id (UUID)
- nom
- prenom
- email
- telephone
- password
- role
- entreprise
- profile (photo)
- is_active
- last_login
- created_at
- updated_at

## 5.2 Rôles

Séparation stricte :

Rôles système
- SUPER_ADMIN
- ADMIN_SYSTEM

Rôles entreprise
- ADMIN
- COMPTABLE
- RESPONSABLE VENTES

## 5.3 Permissions dynamiques

Permissions basées sur :
permissions = {
    "products": ["create", "read", "update"],
    "sales": ["read"],
}

Permission DRF :
class HasRolePermission(BasePermission):
    # Ekigega Backend — Documentation rapide

    Résumé
    -------
    Ekigega Backend est une API Django + Django REST Framework conçue pour des scénarios SaaS multi-tenant.
    Le projet fournit :
    - Authentification JWT (SimpleJWT)
    - Gestion multi-tenant (isolation par entreprise)
    - Rôles et permissions dynamiques
    - Analytics et cache (Redis)
    - Audit logs

    Statut: prêt pour développement et intégration (voir sections ci‑dessous pour l'installation et le workflow développeur).

    Prérequis
    ---------
    - Python 3.11+ (adapter si nécessaire)
    - PostgreSQL (ou autre SGBD ; voir variable d'environnement DB_ENGINE)
    - Redis (optionnel mais recommandé pour le cache)

    Fichiers importants
    -------------------
    - `manage.py` — point d'entrée Django
    - `ekigega/settings.py` — configuration principale (utilise `python-dotenv`)
    - `apps/` — applications Django (accounts, analytics, commerce, core, ...)
    - `pyproject.toml` — configuration des outils (black, isort, ruff, flake8)
    - `.pre-commit-config.yaml` — hooks pour formattage et lint

    Installation rapide (dev)
    ------------------------
    1. Créez et activez un environnement virtuel:

    ```cmd
    python -m venv .venv
    .venv\Scripts\activate
    ```

    2. Installez les dépendances:

    ```cmd
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

    3. Copiez et adaptez le fichier d'environnement:

    ```cmd
    copy .env.example .env
    remplir les variables (DJANGO_SECRET_KEY, DB_*, REDIS_URL ...)
    ```

    4. Appliquez les migrations et démarrez le serveur:

    ```cmd
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

    **Serveurs WSGI disponibles :**
    - **Dev (Windows/Linux)** : `python manage.py runserver` (serveur Django intégré, idéal pour le développement)
    - **Production (Windows)** : `waitress-serve ekigega.wsgi:application`
    - **Production (Linux)** : `gunicorn ekigega.wsgi:application` (installez gunicorn sur Linux via pip)

    Variables d'environnement clés
    ------------------------------
    - `DJANGO_SECRET_KEY` — clé secrète
    - `DJANGO_DEBUG` — True/False
    - `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
    - `REDIS_URL` — pour `django-redis`
    - `JWT_ACCESS_TOKEN_LIFETIME_DAYS`, `JWT_REFRESH_TOKEN_LIFETIME_DAYS`, etc.

    Tests
    -----
    Le projet utilise `pytest`/`pytest-django` :

    ```cmd
    pytest
    ```

    Linting & formatage (workflow développeur)
    ----------------------------------------
    - Formatage automatique : `black`
    - Tri des imports : `isort`
    - Nettoyage des imports inutilisés : `autoflake`
    - Lint & fixes rapides : `ruff --fix`
    - Vérification finale : `flake8`

    Pré-commit
    ---------
    Les hooks définis dans `.pre-commit-config.yaml` s'exécutent automatiquement lors des commits si vous avez installé pre-commit:

    ```cmd
    pip install pre-commit
    pre-commit install
    pre-commit run --all-files  # exécute tous les hooks sur l'ensemble du dépôt
    ```

    Conseils de sécurité & déploiement
    ---------------------------------
    - **Windows développement** : utilisez `python manage.py runserver`. Gunicorn n'est pas compatible Windows ; utilisez `waitress-serve` si vous avez besoin d'un WSGI spécifique.
    - **Linux/production** : déployez sur une instance Linux (AWS EC2, Azure VM, DigitalOcean, etc.) et utilisez `gunicorn` avec un reverse proxy (nginx, Apache).
    - Ne stockez jamais les secrets dans le dépôt. Utilisez des variables d'environnement ou un secret manager (AWS Secrets Manager, Azure Key Vault, etc.).
    - En production, activez `DEBUG=False`, configurez `ALLOWED_HOSTS`, et servez les fichiers statiques via un CDN ou un serveur dédié.
    - Utilisez une base de données relationnelle (Postgres recommandé).
    - Activez un cache Redis pour les analytics et la mise en cache des calculs lourds.
    - En production, limitez `CORS_ALLOW_ALL_ORIGINS` et configurez `CORS_ALLOWED_ORIGINS` avec vos domaines de frontend spécifiques.

    Structure du projet (abrégée)
    ----------------------------
    `apps/` contient les apps métier : `accounts`, `commerce`, `analytics`, `core`, `tenants`, etc.

    Support & contributions
    -----------------------
    Pour contribuer :
    1. Forker le dépôt
    2. Créer une branche feature/bugfix
    3. S'assurer que les hooks pre-commit passent
    4. Ouvrir une Pull Request avec description et tests si nécessaire

    Contact
    -------
    Mainteneur principal: voir l'auteur du dépôt (GitHub) — ouvrir une issue pour signaler un bug ou demander une fonctionnalité.

    Annexes
    -------
    - `requirements.txt` et `requirements-dev.txt` se trouvent à la racine. Pinnez les versions en CI pour des builds reproductibles.

---

# 6. Documentation détaillée des endpoints

## 6.1 Commerce (`apps/commerce`)

### Modèles

#### UniteMesure
Classe pour représenter une unité de mesure avec facteur de conversion.
- Permet les conversions entre unités sans stocker en base de données
- Attributs: `code`, `label`, `type`, `facteur_conversion`

#### CatalogueUnites
Catalogue centralisé de toutes les unités de mesure disponibles.
- Unités supportées: Poids (t, kg, g, mg), Volume (hL, L, mL), Longueur (m, cm, mm), Unité (unite, paire, piece, carton)
- Méthodes: `get(code)`, `get_choices()`, `get_by_type(type)`

#### Categorie
Modèle pour les catégories de produits.
- Appartient à une entreprise (tenant)
- Permet de classifier les produits

#### Produit
Modèle pour les produits en stock.
- Gère: nom, catégorie, prix, unité de mesure, quantité en stock
- Méthodes de conversion:
  - `convert_quantity_to(qty, target_code)`: Convertir vers une autre unité
  - `convert_quantity_from(qty, source_code)`: Convertir depuis une autre unité
- Exemple: Un produit de 1 kg peut être converti en 1000 g

#### Vente
Modèle pour les ventes (factures/bons de vente).
- Contient: client, statut de paiement, prix total
- Statuts: en_attente, payee, annulee, paiement_partiel, rembourse
- Gère le stock automatiquement (décrémentation à la création, restauration à l'annulation)

#### VenteProduit
Modèle pour les items (lignes) d'une vente.
- Relie une Vente à un Produit
- Contient: quantité vendue, prix unitaire appliqué

### ViewSets et Endpoints

#### CategorieViewSet
```
GET    /api/categories/              - Lister toutes les catégories
POST   /api/categories/              - Créer une catégorie
GET    /api/categories/{id}/         - Détails d'une catégorie
PUT    /api/categories/{id}/         - Remplacer une catégorie
PATCH  /api/categories/{id}/         - Modifier une catégorie
DELETE /api/categories/{id}/         - Supprimer une catégorie
```
Filtres: `nom` | Recherche: `nom` | Tri: `nom`, `created_at`

#### ProduitViewSet
```
GET    /api/produits/                - Lister tous les produits
POST   /api/produits/                - Créer un produit
GET    /api/produits/{id}/           - Détails d'un produit
PUT    /api/produits/{id}/           - Remplacer un produit
PATCH  /api/produits/{id}/           - Modifier un produit
DELETE /api/produits/{id}/           - Supprimer un produit
```
Filtres: `categorie`, `prix` | Recherche: `nom` | Tri: `prix`, `nom`, `created_at`

Unités supportées: kg, g, mg, t, L, mL, hL, m, cm, mm, unite, paire, piece, carton

#### VenteViewSet
```
GET    /api/ventes/                  - Lister toutes les ventes
POST   /api/ventes/                  - Créer une vente
GET    /api/ventes/{id}/             - Détails d'une vente
PATCH  /api/ventes/{id}/             - Modifier une vente
DELETE /api/ventes/{id}/             - Supprimer une vente

Actions personnalisées:
GET    /api/ventes/{id}/items/       - Récupérer les items d'une vente
PATCH  /api/ventes/{id}/mark_paid/   - Marquer comme payée
PATCH  /api/ventes/{id}/mark_cancelled/ - Annuler et restaurer stock
```

Filtres: `statut`, `client` | Recherche: `client__nom`, `client__prenom` | Tri: `created_at`, `statut`, `prix_vente`

**Création d'une vente:**
```json
{
  "client": "550e8400-e29b-41d4-a716-446655440000",
  "statut": "payee",
  "items": [
    {
      "produit": "650e8400-e29b-41d4-a716-446655440001",
      "quantite": 5,
      "unite": "kg",
      "prix_unitaire": 10.50
    }
  ]
}
```

Le système gère automatiquement:
- Conversion de la quantité vers l'unité du produit
- Décrément du stock
- Calcul du prix total (prix_vente)

## 6.2 Partners (`apps/partners`)

### Modèle

#### Partner
Modèle pour les partenaires (clients ou fournisseurs).
- Attributs: type, nom, prenom, email, telephone, adresse
- Types: "client" ou "fournisseur"
- Email unique par entreprise

### ViewSet et Endpoints

#### PartnerViewSet
```
GET    /api/partners/                - Lister tous les partenaires
POST   /api/partners/                - Créer un partenaire
GET    /api/partners/{id}/           - Détails d'un partenaire
PUT    /api/partners/{id}/           - Remplacer un partenaire
PATCH  /api/partners/{id}/           - Modifier un partenaire
DELETE /api/partners/{id}/           - Supprimer un partenaire

Actions personnalisées:
GET    /api/partners/clients/        - Lister uniquement les clients
GET    /api/partners/fournisseurs/   - Lister uniquement les fournisseurs
```

Filtres: `nom`, `email`, `telephone` | Recherche: `nom`, `prenom`, `email` | Tri: `nom`, `created_at`

**Création d'un client:**
```json
{
  "type": "client",
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "telephone": "+33612345678",
  "adresse": "123 Rue de la Paix, 75000 Paris"
}
```

## 6.3 Permissions et Authentification

### Authentification
- JWT Token requis pour tous les endpoints
- Format: `Authorization: Bearer <token>`

### Permissions par rôle
- **Superuser**: Accès complet à toutes les ressources
- **Finance**: Peut créer/modifier les partenaires
- **Sales**: Peut créer/modifier les ventes et produits
- **Read-only**: Accès en lecture seule

### Multi-tenancy
- Chaque utilisateur est associé à une entreprise (tenant)
- Les données sont automatiquement filtrées par tenant
- Les champs `entreprise` sont définis automatiquement lors de la création

## 6.4 Conversions d'unités

Le système supporte les conversions automatiques entre unités du même type.

### Exemple: Vente en unité différente du produit
```python
# Produit stocké en kg
produit = Produit.objects.create(
    nom="Farine",
    mesure="kg",
    prix=2.50,
    quantite=100
)

# Client achète 500g
vente_item = {
    "produit": produit.id,
    "quantite": 500,
    "unite": "g"  # Conversion automatique: 500g = 0.5kg
}

# Le stock sera décrémenté de 0.5 kg
```

### Facteurs de conversion supportés
- **Poids**: 1 t = 1000 kg, 1 kg = 1, 1 g = 0.001, 1 mg = 0.000001
- **Volume**: 1 hL = 100 L, 1 L = 1, 1 mL = 0.001
- **Longueur**: 1 m = 1, 1 cm = 0.01, 1 mm = 0.001
- **Unité**: Toutes les unités = 1 (pas de conversion possible)

## 6.5 Gestion du stock

Le stock est géré automatiquement lors des opérations de vente:

1. **Création d'une vente**:
   - Le stock est décrémenté par la quantité vendue
   - La quantité est convertie vers l'unité du produit si nécessaire
   - Erreur si le stock est insuffisant

2. **Annulation d'une vente**:
   - Le stock est restauré pour tous les items
   - Utilise une transaction atomique pour l'intégrité

3. **Changement de statut**:
   - Les statuts disponibles: en_attente, payee, annulee, paiement_partiel, rembourse
   - Seul le statut peut être modifié après la création (sauf annulation)

## 6.6 Validation et Erreurs

### Validations communes
- **Email unique**: Par entreprise (Partners)
- **Quantité positive**: Doivent être >= 0 (Produits, Ventes)
- **Stock suffisant**: Impossible de vendre plus que le stock disponible
- **Types d'unité compatibles**: Impossible de convertir poids en volume

### Codes d'erreur HTTP
- **200 OK**: Requête réussie
- **201 Created**: Ressource créée avec succès
- **204 No Content**: Ressource supprimée
- **400 Bad Request**: Validation échouée
- **404 Not Found**: Ressource non trouvée
- **409 Conflict**: Types d'unité incompatibles
- **403 Forbidden**: Accès refusé (permissions insuffisantes)

## 6.7 Performance et Indexes

### Indexes de base de données
- **Commerce**:
  - (entreprise, categorie)
  - (entreprise, nom) sur Produit et Categorie
  - (entreprise, statut) sur Vente
  - (entreprise, created_at) sur Vente

- **Partners**:
  - Unique: (entreprise, email)

### Optimisations
- Utilisation de `select_for_update()` lors des modifications de stock
- Transactions atomiques pour les opérations complexes
- Prefetch relations pour réduire les requêtes N+1

## 6.8 Intégration avec d'autres modules

### Tenants
- Chaque ressource appartient à une `Entreprise` (tenant)
- Filtrage automatique par tenant du user

### Accounts
- Authentification via JWT
- Association user ↔ entreprise

### Core
- `BaseModel`: Timestamps (created_at, updated_at)
- `TenantModel`: Héritage + champ entreprise
- Mixins: `TenantQuerySetMixin` pour filtrage automatique
- Permissions: `HasRolePermission`, `IsAuthenticatedAndTenant`

## 6.9 Exemples d'utilisation

### Créer un client et effectuer une vente
```python
# 1. Créer un client
client = Partner.objects.create(
    entreprise=entreprise,
    type="client",
    nom="Dupont",
    email="client@example.com"
)

# 2. Vérifier le stock du produit
produit = Produit.objects.get(nom="Farine")
print(f"Stock: {produit.quantite} kg")

# 3. Créer une vente (API)
POST /api/ventes/
{
    "client": client.id,
    "statut": "payee",
    "items": [{
        "produit": produit.id,
        "quantite": 500,
        "unite": "g",
        "prix_unitaire": 5.00
    }]
}

# 4. Vérifier le nouveau stock
produit.refresh_from_db()
print(f"Nouveau stock: {produit.quantite} kg")  # 99.5 kg

# 5. Annuler la vente
PATCH /api/ventes/{vente_id}/mark_cancelled/

# Stock restauré à 100 kg
```

## 6.10 Notes importantes

1. **Conversions décimales**: Utilisez `Decimal` pour éviter les erreurs de précision
2. **Transaction atomique**: Les ventes utilisent des transactions pour éviter les incohérences
3. **Tenant isolation**: Les données sont strictement isolées par tenant
4. **Permissions**: Vérifiez les rôles avant les opérations sensibles
5. **Unités**: Toujours spécifier l'unité lors de la création d'un produit

---

*Documentation mise à jour: 2026-01-10*


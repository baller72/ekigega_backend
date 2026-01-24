from celery import shared_task
from django.contrib.auth import get_user_model
from apps.commerce.models import Vente, Produit
from apps.finance.models import Depense, Stock
from apps.subscriptions.models import Abonnement
from apps.exports.models import ExportHistory
from apps.exports.utils import export_to_csv, export_to_excel

User = get_user_model()

@shared_task
def scheduled_export(module, format="CSV"):
    user = User.objects.filter(is_superuser=True).first()
    
    if module == "Ventes":
        queryset = Vente.objects.all()
        fields = ["id", "client", "produit", "quantite", "statut", "created_at"]
    elif module == "Produits":
        queryset = Produit.objects.all()
        fields = ["id", "nom", "categorie", "prix", "quantite", "created_at"]
    elif module == "Dépenses":
        queryset = Depense.objects.all()
        fields = ["id", "categorie", "description", "montant", "type", "created_at"]
    elif module == "Stock":
        queryset = Stock.objects.all()
        fields = ["id", "produit", "quantite", "prix_achat", "prix_vente", "created_at"]
    elif module == "Abonnements":
        queryset = Abonnement.objects.all()
        fields = ["id", "client", "plan", "statut", "start_date", "end_date"]
    else:
        return "Module inconnu"

    if format == "CSV":
        filename, content = export_to_csv(queryset, fields)
    else:
        filename, content = export_to_excel(queryset, fields)

    record = ExportHistory.objects.create(user=user, module=module, format=format)
    record.file_url.save(filename, content)
    record.save()
    return f"Export {module} ({format}) créé avec succès"

@shared_task
def scheduled_vente_export():
    # Superuser par défaut pour attribution du fichier export
    user = User.objects.filter(is_superuser=True).first()
    queryset = Vente.objects.all()
    fields = ["id", "client", "produit", "quantite", "statut", "created_at"]

    filename, content = export_to_csv(queryset, fields)
    export_record = ExportHistory.objects.create(user=user, module="Ventes", format="CSV")
    export_record.file_url.save(filename, content)
    export_record.save()
    return f"Export Ventes créé : {export_record.file_url.url}"

@shared_task
def scheduled_vente_export():
    # Superuser par défaut pour attribution du fichier export
    user = User.objects.filter(is_superuser=True).first()
    queryset = Produit.objects.all()
    fields = ["id", "nom", "categorie", "prix", "quantite", "created_at"]

    filename, content = export_to_csv(queryset, fields)
    export_record = ExportHistory.objects.create(user=user, module="Produits", format="CSV")
    export_record.file_url.save(filename, content)
    export_record.save()
    return f"Export Produits créé : {export_record.file_url.url}"


@shared_task
def scheduled_vente_export():
    # Superuser par défaut pour attribution du fichier export
    user = User.objects.filter(is_superuser=True).first()
    queryset = Depense.objects.all()
    fields = ["id", "categorie", "description", "montant", "type", "created_at"]

    filename, content = export_to_csv(queryset, fields)
    export_record = ExportHistory.objects.create(user=user, module="Depense", format="CSV")
    export_record.file_url.save(filename, content)
    export_record.save()
    return f"Export Depense créé : {export_record.file_url.url}"


@shared_task
def scheduled_vente_export():
    # Superuser par défaut pour attribution du fichier export
    user = User.objects.filter(is_superuser=True).first()
    queryset = Abonnement.objects.all()
    fields = ["id", "type", "date_debut", "date_fin", "prix", "statut", "created_at"]

    filename, content = export_to_csv(queryset, fields)
    export_record = ExportHistory.objects.create(user=user, module="Abonnement", format="CSV")
    export_record.file_url.save(filename, content)
    export_record.save()
    return f"Export Abonnement créé : {export_record.file_url.url}"
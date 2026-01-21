from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from apps.exports.serializers import ExportHistorySerializer
from apps.exports.tasks import scheduled_export
from apps.exports.utils import export_to_csv, export_to_excel
from apps.exports.models import ExportHistory

class ExportViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["POST"])
    def generate(self, request):
        module = request.data.get("module")
        format = request.data.get("format", "CSV")
        user = request.user

        # Sélection du queryset selon le module
        if module == "Ventes":
            from apps.commerce.models import Vente
            queryset = Vente.objects.all()
            fields = ["id", "client", "produit", "quantite", "statut", "created_at"]
        elif module == "Depenses":
            from apps.finance.models import Depense
            queryset = Depense.objects.all()
            fields = ["id", "categorie", "description", "montant", "type", "created_at"]
        elif module == "Produits":
            from apps.commerce.models import Produit
            queryset = Produit.objects.all()
            fields = ["id", "nom", "categorie", "prix", "quantite", "created_at"]
        elif module == "Abonnements":
            from apps.subscriptions.models import Abonnement
            queryset = Abonnement.objects.all()
            fields = ["id", "client", "plan", "statut", "start_date", "end_date"]
        # Ajouter Produits et Abonnements
        else:
            return Response({"error": "Module non supporté"}, status=400)

        if format == "CSV":
            filename, content = export_to_csv(queryset, fields)
        elif format == "Excel":
            filename, content = export_to_excel(queryset, fields)
        else:
            return Response({"error": "Format non supporté"}, status=400)

        export_record = ExportHistory.objects.create(
            user=user, module=module, format=format
        )
        export_record.file_url.save(filename, content)
        export_record.save()

        return Response({"file_url": export_record.file_url.url}, status=status.HTTP_200_OK)


class ExportTriggerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        module = request.data.get("module")
        format = request.data.get("format", "CSV")
        scheduled_export.delay(module, format)
        return Response({"message": f"Tâche d'export pour {module} déclenchée."}, status=status.HTTP_202_ACCEPTED)

class ExportHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exports = ExportHistory.objects.all()
        serializer = ExportHistorySerializer(exports, many=True)
        return Response(serializer.data)
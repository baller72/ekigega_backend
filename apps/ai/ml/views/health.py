from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.ai.ml.services.orchestrator import enterprise_health_analysis


class EnterpriseHealthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entreprise = request.user.entreprise
        data = enterprise_health_analysis(entreprise)
        return Response(data)
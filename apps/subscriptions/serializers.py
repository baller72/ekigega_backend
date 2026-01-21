from rest_framework import serializers

from .models import Abonnement


class AbonnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abonnement
        fields = "__all__"
        read_only_fields = ("entreprise",)

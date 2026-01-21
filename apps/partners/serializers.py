from rest_framework import serializers

from .models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = ("entreprise",)

    def create(self, validated_data):
        validated_data["entreprise"] = self.context["request"].user.entreprise
        return super().create(validated_data)

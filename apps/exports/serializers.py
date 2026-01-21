from rest_framework import serializers
from apps.exports.models import ExportHistory

class ExportHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportHistory
        fields = "__all__"
from rest_framework import serializers


class CashflowSerializer(serializers.Serializer):
    cash_in = serializers.FloatField()
    cash_out = serializers.FloatField()
    balance = serializers.FloatField()


class KPISerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    total_ventes = serializers.IntegerField()
    revenus = serializers.FloatField()
    depenses = serializers.FloatField()

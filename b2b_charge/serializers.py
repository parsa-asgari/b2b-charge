from rest_framework import serializers
from .models import Merchant, TransactionLog


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        exclude = ("created_time", "updated_time", "is_active")

class BuyChargeSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    amount = serializers.IntegerField()

    class Meta:
        model = Merchant
        exclude = ("created_time", "updated_time", "is_active")

class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        exclude = ("created_time", "updated_time", "is_active")
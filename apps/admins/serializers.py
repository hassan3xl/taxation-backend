from rest_framework import serializers
# from ..models import Vehicle, Payment
from apps.taxations.models.taxations import Payment, Vehicle
from apps.users.models import (
    TaxPayer
)
from apps.taxations.api import (
    AgentAndAdminVehicleSerializer
)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_method', 'timestamp', 'notes']
    
class CreateVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'owner_name', 'phone_number']


class TaxPayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPayer
        fields = ["full_name", "phone", "address", "created_at", "updated_at"]


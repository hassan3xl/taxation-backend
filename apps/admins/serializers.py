from rest_framework import serializers
# from ..models import Vehicle, Payment
from apps.taxations.models.taxations import Payment, Vehicle
from apps.users.models import (
    TaxPayer
)
from apps.taxations.api import (
    AgentAndAdminVehicleSerializer
)

    
class CreateVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'owner_name', 'phone_number']


class TaxPayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPayer
        fields = ["full_name", "phone", "address", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(
        source="vehicle.plate_number",
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "amount",
            "payment_method",
            "collected_by",
            "timestamp",
            "notes",
        ]
        read_only_fields = ["id", "timestamp"]


class VehicleFinanceSerializer(serializers.ModelSerializer):
    total_expected_revenue = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total_paid = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    current_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    compliance_status = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "plate_number",
            "owner_name",
            "phone_number",
            "is_active",
            "is_approved_by_admin",
            "total_expected_revenue",
            "total_paid",
            "current_balance",
            "compliance_status",
        ]

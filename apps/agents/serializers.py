from rest_framework import serializers
# from ..models import Vehicle, Payment
from apps.core.models import Payment, Vehicle
from apps.users.models import (
    TaxPayer
)
from apps.core.api import (
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


class AgentVehicleSerializer(serializers.ModelSerializer):
    current_balance = serializers.FloatField(read_only=True)
    total_paid = serializers.FloatField(read_only=True)
    total_expected_revenue = serializers.FloatField(read_only=True)
    compliance_status = serializers.ReadOnlyField()
    daily_rate = serializers.FloatField(read_only=True)
    exempted_days_count = serializers.ReadOnlyField() # Useful for agents to see
    
    recent_payments = serializers.SerializerMethodField()
    active_exemption = serializers.SerializerMethodField() # To show if they are currently sick

    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate_number', 'owner_name', 'phone_number', 
            'created_at', 'is_active', 'is_approved_by_admin', 'activated_at', 
            'current_balance', 'total_paid', 'total_expected_revenue',
            'daily_rate', 'compliance_status', 'exempted_days_count',
            'active_exemption',
            'recent_payments'
        ]

    def get_recent_payments(self, obj):
        payments = obj.payments.order_by('-timestamp')[:3]
        return PaymentSerializer(payments, many=True).data

    def get_active_exemption(self, obj):
        """
        Check if there is an approved exemption currently active today.
        This helps agents know not to harass someone who is officially 'sick'.
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        exemption = obj.exemptions.filter(
            is_approved=True, 
            start_date__lte=today, 
            end_date__gte=today
        ).first()
        
        if exemption:
            return {
                "is_exempt": True,
                "reason": exemption.get_reason_display(),
                "end_date": exemption.end_date
            }
        return None

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

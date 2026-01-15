from rest_framework import serializers
from apps.core.models import Payment, Vehicle, VehicleExemption

class VehicleExemptionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = VehicleExemption
        fields = [
            'id', 'vehicle', 'start_date', 'end_date', 
            'reason', 'reason_display', 'description', 
            'is_approved', 'created_at'
        ]
        read_only_fields = ['is_approved', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_method', 'timestamp', 'notes']


class PublicVehicleSerializer(serializers.ModelSerializer):
    compliance_status = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate_number', 'current_balance', 'owner_name', 'phone_number', 
            'created_at', 'is_active', 'is_approved_by_admin', 'activated_at', 
            'daily_rate', 'compliance_status'
        ]

    
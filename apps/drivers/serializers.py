from rest_framework import serializers
from apps.core.models import Payment, Vehicle, VehicleExemption



class DriverPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_method', 'driver', 'timestamp', 'notes']


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


# --- 3. Taxpayer Vehicle Serializer (For the User App) ---
class TaxpayerVehicleSerializer(serializers.ModelSerializer):
    current_balance = serializers.FloatField(read_only=True)
    compliance_status = serializers.ReadOnlyField() # The new 7-day rule status
    daily_rate = serializers.FloatField(read_only=True)
    
    recent_payments = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate_number', "owner", 'owner_name', 'phone_number', 'qr_code',
            'is_active', 'created_at',
            'current_balance', 'daily_rate',
            'compliance_status', 
            'recent_payments'
        ]

    def get_recent_payments(self, obj):
        payments = obj.payments.order_by('-timestamp')[:5] # Increased to 5 for better context
        return PaymentSerializer(payments, many=True).data

    def qr_code(self, obj):
        return obj.qr_code.url if obj.qr_code else None


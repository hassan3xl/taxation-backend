from rest_framework import serializers
from apps.taxations.models.taxations import Payment, Vehicle, VehicleExemption

# --- 1. Exemption Serializer (For Sickness/Theft Reports) ---
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


# --- 2. Payment Serializer ---
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


# --- 4. Agent/Admin Vehicle Serializer (For the Dashboard) ---
class AgentAndAdminVehicleSerializer(serializers.ModelSerializer):
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
    
from rest_framework import (
    viewsets, 
    status, 
    filters, 
    generics, 
    permissions
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from apps.users.models import  TaxPayer
import random
from utils.permissions import (
    IsAgent, 
    IsTaxPayer
)
from apps.core.models import(
    Vehicle, 
    Payment
)
from .serializers import (
    PaymentSerializer, 
    PublicVehicleSerializer
)

class PublicVehicleViews(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = PublicVehicleSerializer
    permission_classes = [permissions.AllowAny]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number', 'phone_number']
    lookup_field = 'plate_number' 

    def retrieve(self, request, *args, **kwargs):
        vehicle = get_object_or_404(
            Vehicle,
            plate_number__iexact=kwargs[self.lookup_field]
        )

        if not vehicle.is_active:
            return Response(
                {
                    "detail": "This vehicle is currently inactive.",
                    "code": "VEHICLE_INACTIVE"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)



class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all().order_by('-timestamp')
    serializer_class = PaymentSerializer


# Mock function for sending SMS (Replace with Twilio/Termii/KudiSMS later)
def send_sms_otp(phone, otp):
    print(f"--- SENDING OTP {otp} TO {phone} ---")
    return True

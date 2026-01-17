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
    TaxpayerVehicleSerializer,
)

class TaxpayerVehicleListView(generics.ListAPIView):
    """
    Returns a list of ALL vehicles owned by the currently logged-in TaxPayer.
    """
    serializer_class = TaxpayerVehicleSerializer
    permission_classes = [IsTaxPayer]
    
    def get_queryset(self):
        # 1. Get the TaxPayer profile associated with the logged-in User
        taxpayer = get_object_or_404(TaxPayer, user=self.request.user)
        # 2. Return all vehicles linked to this TaxPayer
        return Vehicle.objects.filter(owner=taxpayer).order_by('-created_at')


# Mock function for sending SMS (Replace with Twilio/Termii/KudiSMS later)
def send_sms_otp(phone, otp):
    print(f"--- SENDING OTP {otp} TO {phone} ---")
    return True

class ClaimProfileView(APIView):
    permission_classes = [IsTaxPayer]
    
    def get(self, request, plate_number):
        plate_number = plate_number.upper().strip()
        
        # --- CHECK 1: Does THIS user already have a vehicle? ---
        # Assuming your TaxPayer model is linked to User, and Vehicle is linked to TaxPayer
        # Adjust 'taxpayer' to whatever related_name you use (e.g., request.user.taxpayer_profile)
        try:
            current_taxpayer = request.user.taxpayer 
            if hasattr(current_taxpayer, 'vehicle') and current_taxpayer.vehicle:
                return Response(
                    {"error": "You have already linked a vehicle to this account. You cannot own more than one."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except AttributeError:
            # Handle case where user might not be set up correctly as a taxpayer yet
            pass

        # --- CHECK 2: Find the vehicle ---
        try:
            vehicle = Vehicle.objects.get(plate_number=plate_number)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Vehicle not found. Please check the plate number."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # --- CHECK 3: Is the vehicle already owned? ---
        if vehicle.owner is not None:
            # Whether it's the current user OR another user, in the context of "Claiming",
            # this is an error. We do not want to return 200 OK here.
            return Response(
                {"error": "This vehicle has already been claimed."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # --- CHECK 4: "Ghost" Vehicles (No phone number to verify with) ---
        if not vehicle.phone_number:
            return Response(
                {"error": "Vehicle exists but has no contact info. Visit our office to update details."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Success Response
        masked_phone = f"{vehicle.phone_number[:4]}****{vehicle.phone_number[-3:]}"
        # safe split in case name is single word
        name_parts = vehicle.owner_name.split()
        masked_name = f"{name_parts[0]} ***" if name_parts else "***"

        return Response({
            "found": True,
            "plate_number": vehicle.plate_number,
            "masked_owner": masked_name,
            "masked_phone": masked_phone,
            "vehicle_id": vehicle.id,
            "status": vehicle.is_active,
            # "make": vehicle.make, # Ensure you send these if frontend uses them
            # "model": vehicle.model,
            "message": "Vehicle found."
        }, status=status.HTTP_200_OK)

    
class RequestOTPView(APIView):
    permission_classes = [IsTaxPayer]

    def post(self, request):
        vehicle_id = request.data.get("vehicle_id")
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        tax_payer = vehicle.owner

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))
        print(f"--- OTP: {otp} ---")
        
        # Store OTP in session or Redis (Simple session usage here)
        # In production, use Redis with a 5-minute expiry
        request.session['verification_otp'] = otp
        request.session['verification_vehicle_id'] = str(vehicle.id)
        request.session.set_expiry(300) # 5 minutes

        # Send SMS to the database phone, NOT the user input phone
        send_sms_otp(vehicle.phone_number, otp)

        return Response({
                "message": "OTP sent to your registered phone number.",
                "otp for dev": otp}, 
                status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = [IsTaxPayer]
    
    def post(self, request):
        user_otp = request.data.get("otp")
        session_otp = request.session.get('verification_otp')
        vehicle_id_session = request.session.get('verification_vehicle_id')

        # 1. Validate OTP
        if not session_otp or user_otp != session_otp:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Get the Vehicle
        vehicle = get_object_or_404(Vehicle, id=vehicle_id_session)

        # 3. Get the TaxPayer Profile for the current User
        # We use get_or_create to be safe, in case the signal didn't run earlier
        tax_payer_profile, created = TaxPayer.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'phone': vehicle.phone_number, # Autofill phone from vehicle if creating new
            }
        )

        # 4. Link the Vehicle to the TaxPayer (NOT the User directly)
        vehicle.owner = tax_payer_profile
        vehicle.save()
        
        # Optional: Sync details if the profile was empty
        if not tax_payer_profile.phone and vehicle.phone_number:
            tax_payer_profile.phone = vehicle.phone_number
            tax_payer_profile.save()

        # Cleanup Session
        del request.session['verification_otp']
        del request.session['verification_vehicle_id']

        return Response({
            "success": True, 
            "message": "Account successfully linked! You can now pay taxes."
        })
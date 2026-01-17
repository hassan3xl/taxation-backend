import tempfile
import random
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
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import qrcode

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

def verify_receipt_public(request, reference):
    """
    Public Page: Anyone scanning the QR code lands here.
    It shows Green (Valid) or Red (Invalid/Fake).
    """
    try:
        payment = Payment.objects.get(refrence=reference)
        context = {
            "valid": payment.payment_status == 'success',
            "payment": payment,
            "vehicle": payment.vehicle,
            "agent": payment.collected_by or "Online"
        }
    except Payment.DoesNotExist:
        context = {"valid": False}
    
    # You will need a simple HTML template for this (see step 4)
    return render(request, 'receipt_verification.html', context)


def generate_pdf_receipt(request, reference):
    """
    Generates a PDF receipt with a QR code for a specific payment.
    """
    payment = get_object_or_404(Payment, refrence=reference)
    
    # 1. Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{reference}.pdf"'

    # 2. Setup the Canvas
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # --- DESIGN ---
    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 50, "TAX PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Date: {payment.timestamp.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(50, height - 120, f"Reference: {payment.refrence}")
    
    # Vehicle Details
    p.line(50, height - 130, 550, height - 130)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 160, "Vehicle Details")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 180, f"Plate Number: {payment.vehicle.plate_number}")
    # Add Vehicle Model/Color if available in your model
    # p.drawString(50, height - 200, f"Model: {payment.vehicle.model}")

    # Payment Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 230, "Payment Details")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 250, f"Amount Paid: NGN {payment.amount}")
    p.drawString(50, height - 270, f"Method: {payment.get_payment_method_display()}")
    p.drawString(50, height - 290, f"Status: {payment.payment_status.upper()}")

    # --- QR CODE GENERATION ---
    # The QR code contains the URL to the verification view
    # Change 'localhost:8000' to your real domain in production
    verify_url = request.build_absolute_uri(f'/api/public/verify/{reference}/')
    
    qr = qrcode.make(verify_url)
    
    # Save QR to a temporary file to draw it on PDF
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        qr.save(tmp.name)
        # Draw the image (x, y, width, height)
        p.drawImage(tmp.name, 400, height - 250, 150, 150)
        p.drawString(420, height - 265, "Scan to Verify")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(150, 50, "This is an electronically generated receipt.")

    # 3. Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
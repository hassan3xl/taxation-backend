from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from utils.payments_utils import PaystackGateway
from apps.core.models import Payment, Vehicle
import uuid

class InitializePaymentView(APIView):
    """
    Endpoint to start a payment.
    Payload: { "vehicle_id": 1, "amount": 500, "payment_method": "online" }
    """
    def post(self, request):
        data = request.data
        vehicle_id = data.get('vehicle_id')
        amount = data.get('amount')
        method = data.get('payment_method', 'online')

        # 1. Validation (Basic)
        if not vehicle_id or not amount:
            return Response({"error": "Vehicle ID and Amount are required"}, status=400)

        # 2. Generate a unique reference for tracking
        # We assume the user is the driver making the payment
        user = request.user 
        ref = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        # 3. Create the Pending Payment Record
        payment = Payment.objects.create(
            vehicle_id=vehicle_id,
            driver=user, #if user.is_authenticated else None, # Handle anonymous if needed
            amount=amount,
            payment_method=method,
            refrence=ref, # Using your spelling
            payment_status='pending'
        )

        # 4. Handle Logic based on Method
        if method == 'online':
            # Use our Mock Gateway
            email = user.email if user.is_authenticated else "guest@example.com"
            paystack_response = PaystackGateway.initialize_payment(email, amount, ref)
            
            if paystack_response['status']:
                return Response({
                    "id": payment.id,
                    "message": "Payment initialized",
                    "payment_url": paystack_response['data']['authorization_url'],
                    "reference": ref
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Payment gateway error"}, status=400)

        elif method == 'agent':
            # If cash, it might be marked success immediately or pending agent approval
            # For now, let's assume agent sets it to success
            payment.payment_status = 'success'
            payment.collected_by = f"Agent-{user.id}" # Assuming current user is agent
            payment.save()
            return Response({"message": "Cash payment recorded successfully"}, status=201)

        return Response({"error": "Invalid payment method"}, status=400)


class VerifyPaymentView(APIView):
    """
    Endpoint the Frontend calls after Paystack redirects back.
    Payload: { "reference": "PAY-..." }
    """
    def post(self, request):
        ref = request.data.get('reference')
        
        if not ref:
            return Response({"error": "No reference provided"}, status=400)

        payment = get_object_or_404(Payment, refrence=ref)

        if payment.payment_status == 'success':
            return Response({"message": "Payment already verified"}, status=200)

        # Call our Gateway to check real status
        is_successful = PaystackGateway.verify_payment(ref)

        if is_successful:
            payment.payment_status = 'success'
            payment.save()
            return Response({"message": "Payment successful!", "status": "success"}, status=200)
        else:
            payment.payment_status = 'failed'
            payment.save()
            return Response({"message": "Payment failed verification", "status": "failed"}, status=400)
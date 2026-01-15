import uuid
import secrets

# Placeholder for when you have keys
PAYSTACK_SECRET_KEY = "sk_test_xxxx" 

class PaystackGateway:
    """
    Service class to handle Paystack logic.
    Currently mocks responses so you can build the frontend.
    """
    
    @staticmethod
    def initialize_payment(email, amount, reference):
        """
        Step 1: Initialize the transaction
        Amount expected in Naira (function converts to Kobo for Paystack if needed)
        """
        # --- MOCK LOGIC (Use this until you have API keys) ---
        print(f"Mocking Paystack Initialize for {email} - Amount: {amount}")
        
        return {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": f"https://checkout.paystack.com/preview-mock/{reference}", # Fake URL
                "access_code": secrets.token_hex(8),
                "reference": reference
            }
        }
        
        # --- REAL LOGIC (Uncomment later) ---
        # url = 'https://api.paystack.co/transaction/initialize'
        # headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
        # data = {
        #     'email': email,
        #     'amount': int(amount * 100), # Convert to kobo
        #     'reference': reference
        # }
        # response = requests.post(url, headers=headers, json=data)
        # return response.json()

    @staticmethod
    def verify_payment(reference):
        """
        Step 2: Verify the status of a transaction
        """
        # --- MOCK LOGIC ---
        print(f"Mocking Verification for {reference}")
        return True # We assume it always succeeds for testing

        # --- REAL LOGIC (Uncomment later) ---
        # url = f'https://api.paystack.co/transaction/verify/{reference}'
        # headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
        # response = requests.get(url, headers=headers)
        # response_data = response.json()
        # if response_data['status'] and response_data['data']['status'] == 'success':
        #     return True
        # return False
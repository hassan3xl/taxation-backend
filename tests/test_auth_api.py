import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_registration_api():
    # 1. Setup the Client (like a fake Postman)
    client = APIClient()
    
    payload = {
        "email": "apiuser@test.com",
        "password1": "strongpassword123",
        "password1": "strongpassword123" # Matching your serializer requirements
    }
    
    # 2. Hit the API
    response = client.post('/api/v1/auth/registration/', payload)
    
    # 3. Check Results
    assert response.status_code == 201
    assert "access" in response.data # Check if we got a token back
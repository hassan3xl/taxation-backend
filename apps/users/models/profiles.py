from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class TaxPayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    # This is the link to the App Account. 
    # It is NULL when uploaded by ministry, and FILLED when user registers/claims.
    user = models.OneToOneField("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="tax_payer_profile")
    
    full_name = models.CharField(max_length=100) 
    phone = models.CharField(max_length=20)     
    address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


# --- Agent (If you need specific agent details) ---
class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("users.", on_delete=models.CASCADE, related_name="agent_profile")
    full_name = models.CharField(max_length=100)
    station_location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.full_name
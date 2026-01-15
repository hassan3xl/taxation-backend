from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

# --- User & Manager (Kept mostly the same) ---
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("taxpayer", "Taxpayer"),
        ("agent", "Agent"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = None
    email = models.EmailField(unique=True)

    # Distinguish between regular users and agents via flags or groups
    role = models.CharField(max_length=100, blank=True, choices=ROLE_CHOICES, default="taxpayer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

class TaxPayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tax_payer_profile")
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent_profile")
    full_name = models.CharField(max_length=100)
    station_location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.full_name
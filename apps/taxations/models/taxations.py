from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from decimal import Decimal
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
import uuid
import datetime

class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # user logic ...
    owner = models.ForeignKey("users.TaxPayer", on_delete=models.CASCADE, related_name="vehicles", null=True, blank=True)
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    
    daily_rate = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    # This field handles the "Soft" delete or permanent ban
    # If they are just owing money, this stays True, but we flag them visually
    is_active = models.BooleanField(default=True)
    is_approved_by_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.plate_number} - {self.owner_name}"

    def save(self, *args, **kwargs):
        self.plate_number = self.plate_number.upper().strip()

        # Detect activation moment
        if self.is_active and self.is_approved_by_admin and self.activated_at is None:
            self.activated_at = timezone.now()

        if not self.qr_code:
            qr_image = qrcode.make(self.plate_number).convert("RGB")

            canvas_size = 290
            canvas = Image.new("RGB", (canvas_size, canvas_size), "white")

            qr_width, qr_height = qr_image.size
            pos = (
                (canvas_size - qr_width) // 2,
                (canvas_size - qr_height) // 2,
            )

            canvas.paste(qr_image, pos)

            buffer = BytesIO()
            canvas.save(buffer, format="PNG")
            buffer.seek(0)

            file_name = f"qr_{self.plate_number}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)


    @property
    def days_since_activation(self):
        """
        Calculates calendar days since vehicle became active.
        """
        if not self.activated_at:
            return 0

        today = timezone.now().date()
        activation_date = self.activated_at.date()

        delta = today - activation_date
        days_active = delta.days + 1  # include today

        activation_hour = timezone.localtime(self.activated_at).hour
        if activation_hour >= 16:
            days_active -= 1

        return max(days_active, 0)

    @property
    def exempted_days_count(self):
        """
        Calculates how many days this vehicle was 'excused' from tax
        due to sickness, theft, or repairs.
        """
        approved_exemptions = self.exemptions.filter(is_approved=True)
        total_days = 0
        for exemption in approved_exemptions:
            # We cap the end_date at 'today' to avoid calculating future exemptions
            # that haven't happened yet, though usually exemptions are past/present.
            end = min(exemption.end_date, timezone.now().date())
            if end >= exemption.start_date:
                duration = (end - exemption.start_date).days + 1
                total_days += duration
        return total_days

    @property
    def total_expected_revenue(self):
        """
        (Total Days - Excused Days) * Daily Rate
        """
        if not self.is_active:
            return 0
            
        # Use the smart logic above
        chargeable_days = self.days_since_activation - self.exempted_days_count
        
        # Safety check to prevent negative bills
        chargeable_days = max(chargeable_days, 0)
        
        return Decimal(chargeable_days) * self.daily_rate

    @property
    def total_paid(self):
        """Sum of all verified payments."""
        result = self.payments.aggregate(total=Sum('amount'))
        return result['total'] or 0.0

    @property
    def current_balance(self):
        return Decimal(str(self.total_paid)) - Decimal(str(self.total_expected_revenue))

    @property
    def compliance_status(self):
        """
        Returns the status based on your 7-day rule.
        """
        balance = self.current_balance
        daily_rate = self.daily_rate
        
        # If balance is positive, they are good
        if balance >= 0:
            return "ACTIVE"
            
        # Check debt depth
        # If they owe more than 7 days worth of tax:
        debt_limit = -(daily_rate * 7)
        
        if balance < debt_limit:
            return "INACTIVE_DUE_TO_DEBT" # The 7-day rule trigger
        
        return "OWING" # Owing, but less than 7 days (e.g. 2 days missed)
    
    
# New Model for Sickness/Theft
class VehicleExemption(models.Model):
    REASON_CHOICES = [
        ('sickness', 'Medical Issue / Sickness'),
        ('mechanical', 'Major Mechanical Breakdown'),
        ('theft', 'Vehicle Stolen'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="exemptions")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True) # e.g., "Leg broken, hospital report attached"
    
    # Admin must approve this for the tax to actually stop counting
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.reason} ({self.start_date} to {self.end_date})"


    
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('agent', 'Agent Cash'),
        ('online', 'Online Payment'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    vehicle = models.ForeignKey(Vehicle, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='agent')
    
    # Track the agent if cash was collected
    collected_by = models.CharField(max_length=100, blank=True, null=True, help_text="Agent ID if cash payment")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"₦{self.amount} - {self.vehicle.plate_number}"
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
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.plate_number = self.plate_number.upper().strip()

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
    def days_since_registration(self):
        """
        Calculates calendar days active with Late Registration Forgiveness.
        """
        # 1. Get simple dates (ignores hours/minutes)
        today = timezone.now().date()
        created_date = self.created_at.date()
        
        # 2. Calculate raw calendar days (Jan 13 - Jan 12 = 1 day)
        delta = today - created_date
        days_active = delta.days + 1  # Add 1 to include today
        
        # 3. Late Registration Check (Grace Period)
        # If they registered after 4 PM (16:00), we don't bill the first day.
        # We check the hour of created_at (in local time ideally, or UTC if that's your setup)
        # Note: timezone.localtime ensures we check the hour in Nigeria time, not UTC
        registration_hour = timezone.localtime(self.created_at).hour
        
        if registration_hour >= 16: # 16:00 is 4 PM
            days_active -= 1
            
        # Ensure we never return negative days (e.g. if registered tonight at 8 PM)
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
        chargeable_days = self.days_since_registration - self.exempted_days_count
        
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
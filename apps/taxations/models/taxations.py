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

class Vehicle(models.Model):
    # Standardizing plate number to uppercase to avoid "yl-123" vs "YL-123" issues
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey("users.TaxPayer", on_delete=models.CASCADE, related_name="vehicles", null=True, blank=True)

    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    
    # Daily tax rate (flexible, in case government increases it from 150)
    daily_rate = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)
    
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    registration_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.plate_number = self.plate_number.upper().strip()
        super().save(*args, **kwargs)

    @property
    def total_expected_revenue(self):
        """Calculates how much they SHOULD have paid since registration."""
        if not self.is_active:
            return 0
            
        today = timezone.now().date()
        # Ensure we count at least 1 day if they registered today
        days_active = (today - self.registration_date).days
        days_active = max(days_active + 1, 1) # +1 to include today
        
        return days_active * float(self.daily_rate)

    @property
    def total_paid(self):
        """Sum of all verified payments."""
        result = self.payments.aggregate(total=Sum('amount'))
        return result['total'] or 0.0

    from decimal import Decimal

    @property
    def current_balance(self):
        total_paid = Decimal(str(self.total_paid or 0))
        total_expected = Decimal(str(self.total_expected_revenue or 0))
        return total_paid - total_expected


    def __str__(self):
        return f"{self.plate_number} ({self.owner_name})"


    # def save(self, *args, **kwargs):
    #     self.plate_number = self.plate_number.upper().strip()

    #     if not self.qr_code:
    #         qr_image = qrcode.make(self.plate_number).convert("RGB")

    #         canvas_size = 290
    #         canvas = Image.new("RGB", (canvas_size, canvas_size), "white")

    #         qr_width, qr_height = qr_image.size
    #         pos = (
    #             (canvas_size - qr_width) // 2,
    #             (canvas_size - qr_height) // 2,
    #         )

    #         canvas.paste(qr_image, pos)

    #         buffer = BytesIO()
    #         canvas.save(buffer, format="PNG")
    #         buffer.seek(0)

    #         file_name = f"qr_{self.plate_number}.png"
    #         self.qr_code.save(file_name, File(buffer), save=False)

    #     super().save(*args, **kwargs)


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
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

class VehicleFinanceService:
    """
    Service to handle complex financial calculations and compliance status for Vehicles.
    Extracted from the Vehicle model to improve testability and separation of concerns.
    """

    @staticmethod
    def calculate_days_since_activation(vehicle):
        """
        Calculates calendar days since vehicle became active.
        """
        if not vehicle.activated_at:
            return 0

        today = timezone.now().date()
        activation_date = vehicle.activated_at.date()

        delta = today - activation_date
        days_active = delta.days + 1  # include today

        # Logic: If activated late in the day (after 4 PM), don't count the first day?
        # Preserving original logic from model:
        activation_hour = timezone.localtime(vehicle.activated_at).hour
        if activation_hour >= 16:
            days_active -= 1

        return max(days_active, 0)

    @staticmethod
    def calculate_exemptions(vehicle):
        """
        Calculates how many days this vehicle was 'excused' from tax
        due to sickness, theft, or repairs.
        """
        # We assume 'exemptions' is a related manager on the vehicle
        approved_exemptions = vehicle.exemptions.filter(is_approved=True)
        total_days = 0
        now_date = timezone.now().date()

        for exemption in approved_exemptions:
            # We cap the end_date at 'today' to avoid calculating future exemptions
            # that haven't happened yet, though usually exemptions are past/present.
            end = min(exemption.end_date, now_date)
            
            # Ensure we don't calculate negative ranges if start_date is in future
            if end >= exemption.start_date:
                duration = (end - exemption.start_date).days + 1
                total_days += duration
        
        return total_days

    @staticmethod
    def calculate_expected_revenue(vehicle):
        """
        (Total Days - Excused Days) * Daily Rate
        """
        if not vehicle.is_active:
            return Decimal("0.00")
            
        days_active = VehicleFinanceService.calculate_days_since_activation(vehicle)
        exempted_days = VehicleFinanceService.calculate_exemptions(vehicle)
        
        chargeable_days = days_active - exempted_days
        
        # Safety check to prevent negative bills
        chargeable_days = max(chargeable_days, 0)
        
        return Decimal(chargeable_days) * vehicle.daily_rate

    @staticmethod
    def calculate_total_paid(vehicle):
        """
        Sum of all verified payments.
        """
        # We assume 'payments' is a related manager
        result = vehicle.payments.aggregate(total=Sum('amount'))
        return result['total'] or Decimal("0.00")

    @staticmethod
    def calculate_current_balance(vehicle):
        """
        Total Paid - Total Expected Revenue
        """
        total_paid = VehicleFinanceService.calculate_total_paid(vehicle)
        expected = VehicleFinanceService.calculate_expected_revenue(vehicle)
        
        # Ensure Decimals
        return Decimal(str(total_paid)) - Decimal(str(expected))

    @staticmethod
    def get_compliance_status(vehicle):
        """
        Returns the status based on the 7-day rule.
        """
        balance = VehicleFinanceService.calculate_current_balance(vehicle)
        daily_rate = vehicle.daily_rate
        
        # If balance is positive or zero, they are good
        if balance >= 0:
            return "ACTIVE"
            
        # Check debt depth
        # If they owe more than 7 days worth of tax:
        debt_limit = -(daily_rate * 7)
        
        if balance < debt_limit:
            return "INACTIVE_DUE_TO_DEBT" # The 7-day rule trigger
        
        return "OWING" # Owing, but less than 7 days (e.g. 2 days missed)

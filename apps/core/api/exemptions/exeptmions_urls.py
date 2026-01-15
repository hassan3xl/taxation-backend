from django.urls import path
from .exeption_views import (
    ExemptionCreateView, 
    PendingExemptionListView, 
    ExemptionActionView,
    VehicleExemptionHistoryView
)

urlpatterns = [
    
    # 1. Agent/Admin files a complaint
    path('exemptions/apply/', ExemptionCreateView.as_view(), name='apply-exemption'),
    
    # 2. Admin dashboard sees this list
    path('exemptions/pending/', PendingExemptionListView.as_view(), name='pending-exemptions'),
    
    # 3. Admin clicks "Approve" or "Reject" on a specific ID
    path('exemptions/<int:pk>/action/', ExemptionActionView.as_view(), name='action-exemption'),
    
    # 4. View history for a specific car (e.g., when viewing car details)
    path('exemptions/<uuid:vehicle_id>/vehicles/', VehicleExemptionHistoryView.as_view(), name='vehicle-exemptions'),
]
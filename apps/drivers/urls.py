from django.urls import path
from .payments.views import (
    InitializePaymentView, 
    VerifyPaymentView
)
from .views import (
    ClaimProfileView, 
    RequestOTPView, 
    VerifyOTPView,
    TaxpayerVehicleListView,
    
)

urlpatterns = [
    path('payments/initialize/', InitializePaymentView.as_view(), name='init_payment'),

    path('payments/verify/', VerifyPaymentView.as_view(), name='verify_payment'),
    
    path('my-vehicles/', TaxpayerVehicleListView.as_view(), name='my-vehicles'),

    path('claim/request-otp/', RequestOTPView.as_view(), name='request-otp'),

    path('claim/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    path('claim/<str:plate_number>/', ClaimProfileView.as_view(), name='claim-profile'),
]


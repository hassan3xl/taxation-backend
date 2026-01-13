from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AgentVehicleViewSet, 
    PaymentViewSet,
    ClaimProfileView, 
    RequestOTPView, 
    VerifyOTPView,
    TaxpayerVehicleListView,
    PublicVehicleViews
    
)

agent_router = DefaultRouter()
agent_router.register(r'vehicles', AgentVehicleViewSet, basename='agent-vehicles')
agent_router.register(r'payments', PaymentViewSet)
agent_router.register(r'public', PublicVehicleViews)


urlpatterns = [

    path('my-vehicles/', TaxpayerVehicleListView.as_view(), name='my-vehicles'),

    # Step 2: Request the OTP (POST)
    path('claim/request-otp/', RequestOTPView.as_view(), name='request-otp'),

    # Step 3: Verify OTP and Link Account (POST)
    path('claim/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    # Step 1: Search for the vehicle (GET)
    path('claim/<str:plate_number>/', ClaimProfileView.as_view(), name='claim-profile'),
]

urlpatterns += [
    path('agent/', include(agent_router.urls)),
]

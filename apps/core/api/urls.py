from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    PublicVehicleViews,
    generate_pdf_receipt, 
    verify_receipt_public
)

core_router = DefaultRouter()
core_router.register(r'payments', PaymentViewSet)
core_router.register(r'vehicles', PublicVehicleViews)



urlpatterns = [
    path('public/', include(core_router.urls)),
    path('receipt/download/<str:reference>/', generate_pdf_receipt, name='download_receipt'),
    path('public/verify/<str:reference>/', verify_receipt_public, name='verify_receipt'),
]



from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet, 
    VehicleViewSet, 
    TaxpayerViewset,
    UsersViewset

)
# agent imports


router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='admin-vehicles')
router.register(r'payments', PaymentViewSet, basename='admin-payments')
router.register(r'taxpayers', TaxpayerViewset, basename='admin-taxpayers')
router.register(r'users', UsersViewset, basename='admin-users')



urlpatterns = [
    path('', include(router.urls)),

]
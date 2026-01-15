from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    PublicVehicleViews
)

core_router = DefaultRouter()
core_router.register(r'payments', PaymentViewSet)
core_router.register(r'vehicles', PublicVehicleViews)



urlpatterns = [
    path('public/', include(core_router.urls)),
]

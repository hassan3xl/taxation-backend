from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # PaymentViewSet, 
    VehicleViewSet, 
    # TaxpayerViewset,
    UsersViewset,
    AdminPaymentListView,
    AdminPaymentDetailView,
    AdminPaymentUpdateView,
    AdminPaymentDeleteView,
    AdminVehicleFinanceListView,
    AdminFinanceDashboardView
)


router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='admin-vehicles')
# router.register(r'payments', PaymentViewSet, basename='admin-payments')
# router.register(r'taxpayers', TaxpayerViewset, basename='admin-taxpayers')
router.register(r'users', UsersViewset, basename='admin-users')


urlpatterns = [
    path('vehicles/<uuid:id>/approve/', VehicleViewSet.as_view({'post': 'approve_vehicle'}), name='approve-vehicle'),
    path("vehicles/finance/", AdminVehicleFinanceListView.as_view()),

    # Payments
    path("payments/", AdminPaymentListView.as_view()),
    path("payments/<uuid:pk>/", AdminPaymentDetailView.as_view()),
    path("payments/<uuid:pk>/update/", AdminPaymentUpdateView.as_view()),
    path("payments/<uuid:pk>/delete/", AdminPaymentDeleteView.as_view()),


    # Dashboard
    path("finance/dashboard/", AdminFinanceDashboardView.as_view()),

]


urlpatterns += [
    path('', include(router.urls)),

]
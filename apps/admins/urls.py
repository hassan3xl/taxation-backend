from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # PaymentViewSet, 
    VehicleViewSet, 
    # TaxpayerViewset,
    # UsersViewset,
    PromoteToAgentView,
    PotentialAgentsListView,
    AdminPaymentListView,
    AdminPaymentDetailView,
    AdminPaymentUpdateView,
    AdminPaymentDeleteView,
    AdminDashboardView,
    AdminFinanceDashboardView,
    AgentDetailView,
    AgentListView
)


router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='admin-vehicles')
# router.register(r'payments', PaymentViewSet, basename='admin-payments')
# router.register(r'taxpayers', TaxpayerViewset, basename='admin-taxpayers')
# router.register(r'users', UsersViewset, basename='admin-users')


urlpatterns = [
    
    path('users/candidates/', PotentialAgentsListView.as_view(), name='agent_candidates'),
    path('users/promote/', PromoteToAgentView.as_view(), name='promote_agent'),

    # agents
    path('agents/', AgentListView.as_view(), name='agent_list'),
    path('agents/<uuid:id>/', AgentDetailView.as_view(), name='agent_detail'),
    
    # vehicles
    path('vehicles/<uuid:id>/approve/', VehicleViewSet.as_view({'post': 'approve_vehicle'}), name='approve-vehicle'),
    # path("vehicles/finance/", AdminVehicleFinanceListView.as_view()),

    # Payments
    path("payments/", AdminPaymentListView.as_view()),
    path("payments/<uuid:pk>/", AdminPaymentDetailView.as_view()),
    path("payments/<uuid:pk>/update/", AdminPaymentUpdateView.as_view()),
    path("payments/<uuid:pk>/delete/", AdminPaymentDeleteView.as_view()),


    # Dashboard
    path("dashboard/", AdminDashboardView.as_view()),
    path("dashboard/finance/", AdminFinanceDashboardView.as_view()),



]


urlpatterns += [
    path('', include(router.urls)),

]
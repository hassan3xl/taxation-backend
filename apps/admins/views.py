import random
from rest_framework import (
    viewsets, 
    status, 
    filters, 
    generics, 
    permissions
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.users.models import  (
    TaxPayer,
    User
)
from apps.users.api import (
    UserProfileSerializer
)
from utils.permissions import (
    IsAdmin, 
    
)
from apps.core.models import(
    Vehicle, 
    Payment
)
from .serializers import (
    PaymentSerializer,
    CreateVehicleSerializer,
    VehicleFinanceSerializer,
    AdminVehicleSerializer
)


class UsersViewset(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdmin]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = AdminVehicleSerializer
    permission_classes = [IsAdmin]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number', 'phone_number']
    lookup_field = 'plate_number'      

    def perform_create(self, serializer):
        serializer.save(is_active=True, is_approved_by_admin=True)

    @action(detail=True, methods=['post'])
    def approve_vehicle(self, request, id=None):  
        vehicle = get_object_or_404(
            Vehicle,
            id=id
        )

        if vehicle.is_approved_by_admin:
            return Response(
                {"detail": "Vehicle is already approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle.is_approved_by_admin = True
        vehicle.is_active = True  
        vehicle.save()

        return Response(
            {"detail": "Vehicle has been approved successfully."},
            status=status.HTTP_200_OK
        )


class AdminVehicleFinanceListView(generics.ListAPIView):
    serializer_class = VehicleFinanceSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = Vehicle.objects.all()

        status = self.request.query_params.get("status")

        if status == "owing":
            qs = [v for v in qs if v.compliance_status == "OWING"]
        elif status == "inactive":
            qs = [v for v in qs if v.compliance_status == "INACTIVE_DUE_TO_DEBT"]
        elif status == "active":
            qs = [v for v in qs if v.compliance_status == "ACTIVE"]

        return qs

class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related("vehicle").order_by("-timestamp")
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "payment_method",
        "vehicle",
        "collected_by",
    ]

    search_fields = [
        "vehicle__plate_number",
        "collected_by",
    ]

    ordering_fields = ["timestamp", "amount"]


class AdminPaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.select_related("vehicle")
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]


class AdminPaymentUpdateView(generics.UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]


class AdminPaymentDeleteView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    permission_classes = [IsAdmin]

class AdminFinanceDashboardView(APIView):
    pass
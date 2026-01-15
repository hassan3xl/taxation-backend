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
from rest_framework.views import APIView
from rest_framework import status
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
    AgentAndAdminVehicleSerializer, 
    CreateVehicleSerializer,
    VehicleFinanceSerializer
)
from utils.permissions import (
    IsAgent
)

class AgentVehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = AgentAndAdminVehicleSerializer
    permission_classes = [IsAgent]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number', 'phone_number']
    lookup_field = 'plate_number' 

    def retrieve(self, request, *args, **kwargs):
        vehicle = get_object_or_404(
            Vehicle,
            plate_number__iexact=kwargs[self.lookup_field]
        )

        if not vehicle.is_active:
            return Response(
                {
                    "detail": "This vehicle is currently inactive.",
                    "code": "VEHICLE_INACTIVE"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)

    # modify the vehicle the creation and  make status true if admin created else false
    def perform_create(self, serializer):
        if self.request.user.role == 'agent':
            serializer.save(is_active=False, is_approved_by_admin=False)
        else:
            serializer.save(is_active=True, is_approved_by_admin=True)


    @action(detail=True, methods=['post'])
    def pay(self, request, plate_number=None):

        vehicle = self.get_object()
        
        amount = request.data.get('amount')
        agent_id = request.user
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Record the payment
        Payment.objects.create(
            vehicle=vehicle,
            amount=amount,
            payment_method='agent',
            collected_by=agent_id,
            notes=f"Collected manually via Agent App"
        )

        # Return updated vehicle data (so the frontend updates the balance instantly)
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
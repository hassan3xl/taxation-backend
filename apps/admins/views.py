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
from apps.taxations.models import(
    Vehicle, 
    Payment
)
from .serializers import (
    PaymentSerializer,
    AgentAndAdminVehicleSerializer, 
    TaxPayerSerializer,
    CreateVehicleSerializer
)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('-created_at')
    serializer_class = AgentAndAdminVehicleSerializer
    permission_classes = [IsAdmin]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number', 'phone_number']
    lookup_field = 'plate_number'         

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all().order_by('-timestamp')
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]

class UsersViewset(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdmin]

class TaxpayerViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TaxPayer.objects.all().order_by('-created_at')
    serializer_class = TaxPayerSerializer
    permission_classes = [IsAdmin]


class AdminDashboard(APIView):
    def get(self, serializer):
        pass

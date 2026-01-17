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
from apps.users.models import  (
    TaxPayer,
    User,
    Agent
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
    AgentsSerializer,
    PaymentSerializer,
    CreateVehicleSerializer,
    VehicleFinanceSerializer,
    AdminVehicleSerializer,
    UserSerializer,
    PromoteAgentSerializer
    
)
from apps.admins.services.dashboard import DashboardService
from apps.admins.services.finance import FinanceDashboardService

class AgentListView(generics.ListAPIView):
    """
    Lists all Agents in the system.
    """
    permission_classes = [IsAdmin]
    serializer_class = AgentsSerializer
    queryset = Agent.objects.select_related("user").all().order_by('-created_at')

class AgentDetailView(generics.RetrieveAPIView):
    """
    Retrieve details of a specific user by ID.
    """
    permission_classes = [IsAdmin]
    serializer_class = AgentsSerializer
    queryset = Agent.objects.select_related("user").all()

    lookup_field = 'id'


class PotentialAgentsListView(generics.ListAPIView):
    """
    Returns a list of users with role='taxpayer'.
    The admin sees this list to decide who to make an Agent.
    """
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        # Only show active users who are currently Taxpayers
        return User.objects.filter(role='taxpayer', is_active=True)

from django.db import transaction

class PromoteToAgentView(APIView):
    """
    Payload: { "user_id": "...", "station_location": "Main Market" }
    Action: Changes role to 'agent' and creates Agent profile.
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = PromoteAgentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        station = serializer.validated_data.get('station_location', '')

        user = get_object_or_404(User, id=user_id)

        # Check if already an agent
        if user.role == 'agent':
            return Response({"message": "User is already an Agent."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Update User Role
                user.role = 'agent'
                user.save()

                # 2. Determine Name (Fetch from TaxPayer profile if it exists)
                full_name = f"{user.first_name} {user.last_name}".strip() or user.email
                if hasattr(user, 'tax_payer_profile'):
                    full_name = user.tax_payer_profile.full_name

                # 3. Create Agent Profile
                # We use update_or_create just in case a profile was left over from before
                Agent.objects.update_or_create(
                    user=user,
                    defaults={
                        'full_name': full_name,
                        'station_location': station
                    }
                )

            return Response({
                "message": f"Successfully promoted {full_name} to Agent.",
                "user_id": user.id,
                "new_role": user.role
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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



# class AdminVehicleFinanceListView(generics.ListAPIView):
#     serializer_class = VehicleFinanceSerializer
#     permission_classes = [IsAdmin]

#     def get_queryset(self):
#         status = self.request.query_params.get("status")
#         # return VehicleFinanceListService.get_filtered_vehicles(status)

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

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        period = request.query_params.get('period', '30_days')
        vehicle_id = request.query_params.get('vehicle_id')
        agent_id = request.query_params.get('agent_id')
        
        data = DashboardService.get_dashboard_data(
            period=period,
            vehicle_id=vehicle_id,
            agent_id=agent_id
        )
        return Response(data)
    
class AdminFinanceDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        period = request.query_params.get('period', '30_days')
        vehicle_id = request.query_params.get('vehicle_id')
        agent_id = request.query_params.get('agent_id')
        
        data = FinanceDashboardService.get_dashboard_data(
            period=period,
            vehicle_id=vehicle_id,
            agent_id=agent_id
        )
        return Response(data)
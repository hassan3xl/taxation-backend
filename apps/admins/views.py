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
# from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
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
    PaymentSerializer,
    CreateVehicleSerializer,
    VehicleFinanceSerializer,
    AdminVehicleSerializer,
    UserListSerializer,
    PromoteAgentSerializer
    
)

# class UsersViewset(viewsets.ModelViewSet):
#     serializer_class = [UserProfileSerializer]
#     permission_classes = [IsAdmin]
#     queryset = User.objects.all()


class PotentialAgentsListView(generics.ListAPIView):
    """
    Returns a list of users with role='taxpayer'.
    The admin sees this list to decide who to make an Agent.
    """
    permission_classes = [IsAdmin]
    serializer_class = UserListSerializer
    
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
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Payment.objects.filter(payment_status='success')

        # --- FILTERS (Same as before) ---
        period = request.query_params.get('period', '30_days')
        today = timezone.now()
        
        if period == 'today':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == '3_months':
            start_date = today - timedelta(days=90)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
            
        queryset = queryset.filter(timestamp__gte=start_date)

        vehicle_id = request.query_params.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicle__id=vehicle_id)

        agent_id = request.query_params.get('agent_id')
        if agent_id:
            # FIX 1: Since it's a ForeignKey, we filter by the User's ID
            queryset = queryset.filter(collected_by__id=agent_id)

        # --- AGGREGATIONS ---
        total_revenue = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        total_transactions = queryset.count()
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0

        # Graph Data (Same as before)
        if period == 'year':
            graph_data = (
                queryset
                .annotate(date=TruncMonth('timestamp'))
                .values('date')
                .annotate(total=Sum('amount'))
                .order_by('date')
            )
        else:
            graph_data = (
                queryset
                .annotate(date=TruncDay('timestamp'))
                .values('date')
                .annotate(total=Sum('amount'))
                .order_by('date')
            )

        # --- FIX 2: Agent Leaderboard ---
        # Instead of .values('collected_by'), we use 'collected_by__first_name' (or email)
        # This tells Django to group by the User's Name, not the User Object.
        agent_performance = (
            queryset.filter(payment_method='agent')
            .values('collected_by__email')
            .annotate(
                total_collected=Sum('amount'),
                transaction_count=Count('id')
            )
            .order_by('-total_collected')[:5]
        )

        # Clean up the agent list for the frontend
        top_agents_clean = []
        for agent in agent_performance:
            # Construct a full name string
            name = agent['collected_by__email']
            top_agents_clean.append({
                "collected_by": name if name else "Unknown Agent",
                "total_collected": agent['total_collected'],
                "transaction_count": agent['transaction_count']
            })

        method_breakdown = (
            queryset.values('payment_method')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        recent_transactions = queryset.select_related('vehicle', 'collected_by').order_by('-timestamp')[:10]
        
        # --- FIX 3: Recent Transactions Loop ---
        recent_data = []
        for p in recent_transactions:
            # Check if collected_by exists (it might be None for online payments)
            if p.collected_by:
                agent_name = f"{p.collected_by.first_name} {p.collected_by.last_name}"
            else:
                agent_name = "System/Online"

            recent_data.append({
                "id": p.id,
                "plate_number": p.vehicle.plate_number,
                "amount": p.amount,
                "method": p.get_payment_method_display(),
                "agent": agent_name,  # We pass the STRING name, not the OBJECT
                "date": p.timestamp
            })

        return Response({
            "summary": {
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "average_value": round(avg_transaction, 2)
            },
            "graph_data": list(graph_data),
            "top_agents": top_agents_clean, # Use our cleaned list
            "payment_methods": list(method_breakdown),
            "recent_transactions": recent_data
        })
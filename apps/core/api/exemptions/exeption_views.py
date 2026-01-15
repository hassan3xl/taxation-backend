from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from apps.core.models import Vehicle, VehicleExemption
from ..serializers import VehicleExemptionSerializer

from utils.permissions import (
    IsAgent,
    IsAdmin,
    IsAdminOrAgent
)

# 1. APPLY FOR EXEMPTION (Agents & Admins)
class ExemptionCreateView(generics.CreateAPIView):
    queryset = VehicleExemption.objects.all()
    serializer_class = VehicleExemptionSerializer
    permission_classes = [IsAdminOrAgent]

    def create(self, request, *args, **kwargs):
        # Expected body: { "vehicle_id": "...", "start_date": "...", "end_date": "...", "reason": "...", "description": "..." }
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validations logic
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        
        if start_date > end_date:
            return Response(
                {"error": "Start date cannot be after end date."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Logic: If an Admin creates it, auto-approve it.
        # If an Agent creates it, leave it as pending (is_approved=False).
        is_approved = False
        approved_by = None
        
        if request.user.role == 'admin':
            is_approved = True
            approved_by = request.user

        exemption = serializer.save(
            is_approved=is_approved,
            approved_by=approved_by
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 2. LIST PENDING EXEMPTIONS (Admins)
# Admins need to see what agents have submitted so they can approve/reject.
class PendingExemptionListView(generics.ListAPIView):
    serializer_class = VehicleExemptionSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        # Show only unapproved requests, newest first
        return VehicleExemption.objects.filter(is_approved=False).order_by('-created_at')


# 3. APPROVE / REJECT EXEMPTION (Admins Only)
class ExemptionActionView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        exemption = get_object_or_404(VehicleExemption, pk=pk)
        action = request.data.get('action') # "approve" or "reject"
        
        if action == 'approve':
            exemption.is_approved = True
            exemption.approved_by = request.user
            exemption.save()
            return Response({"message": "Exemption approved. Tax has been recalculated."}, status=status.HTTP_200_OK)
            
        elif action == 'reject':
            # If rejected, we usually just delete the request or mark it as rejected (if you add a status field).
            # For now, let's delete it so the user knows it didn't count.
            exemption.delete() 
            return Response({"message": "Exemption request rejected and removed."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)


# 4. VEHICLE HISTORY (Optional Helper)
# To see previous exemptions for a specific car
class VehicleExemptionHistoryView(generics.ListAPIView):
    serializer_class = VehicleExemptionSerializer
    permission_classes = [IsAdminOrAgent]

    def get_queryset(self):
        vehicle_id = self.kwargs['vehicle_id']
        return VehicleExemption.objects.filter(vehicle_id=vehicle_id).order_by('-start_date')
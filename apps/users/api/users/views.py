from .serializers import (
    UserProfileSerializer,
    TaxPayerSerializer, 
    AgentSerializer
)
from rest_framework import viewsets, generics
from rest_framework import permissions
from utils.permissions import (
    IsAgent, IsTaxPayer
)
from apps.users.models import (
    TaxPayer, User, Agent
)
from django.shortcuts import get_object_or_404


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class TaxpayerProfileView(generics.RetrieveAPIView):
    serializer_class = TaxPayerSerializer
    permission_classes = [IsTaxPayer]

    def get_object(self):
        taxpayer = get_object_or_404(TaxPayer, user=self.request.user)
        return taxpayer

class AgentProfileView(generics.RetrieveAPIView):
    serializer_class = AgentSerializer
    permission_classes = [IsAgent]

    def get_object(self):
        agent = get_object_or_404(Agent, user=self.request.user)
        print("hellos agent", agent)


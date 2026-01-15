from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AgentVehicleViewSet, 
    
)

agent_router = DefaultRouter()
agent_router.register(r'vehicles', AgentVehicleViewSet, basename='agent-vehicles')


urlpatterns = [
    path('', include(agent_router.urls)),
]

from django.urls import path
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from .views import (
    UserProfileView, AgentProfileView, TaxpayerProfileView
)

urlpatterns = [

    path('me/', UserProfileView.as_view(), name='profile'),
    path('taxpayer/', TaxpayerProfileView.as_view(), name='profile'),
    path('agent/', AgentProfileView.as_view(), name='profile'),


]
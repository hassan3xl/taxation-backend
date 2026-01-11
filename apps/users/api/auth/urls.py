from django.urls import path
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from .views import RegisterAPIView

urlpatterns = [
    # 1. Standard Auth (Login, Logout, Password Change, User details)
    path('', include('dj_rest_auth.urls')),

    # 2. Registration (Uses your CustomRegisterSerializer)
    path('register/', RegisterAPIView.as_view(), name='register'),


    # 4. Token Management (The missing link!)
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
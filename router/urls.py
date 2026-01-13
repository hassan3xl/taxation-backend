from django.urls import path, include
from apps.users.api.auth import urls as auth_urls
from apps.users.api.users import urls as users_urls

# agent imports


urlpatterns = [
    path('auth/', include(auth_urls)),
    path('profile/', include(users_urls)),
    # operators 
    path('taxations/', include('apps.taxations.api.urls')),
    path('admin/', include('apps.admins.urls')),



]

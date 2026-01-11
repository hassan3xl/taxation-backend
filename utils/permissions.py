from rest_framework import permissions

class IsAgent(permissions.BasePermission):
    """
    Allows access only to users with the role 'AGENT' (or Admins).
    """
    def has_permission(self, request, view):
        # 1. User must be logged in
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 2. User must be an AGENT or an ADMIN (Superusers always get access)
        return request.user.role == 'agent' or request.user.is_superuser

class IsTaxPayer(permissions.BasePermission):
    """
    Allows access only to users with the role 'taxpayer' (TaxPayers).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'taxpayer'
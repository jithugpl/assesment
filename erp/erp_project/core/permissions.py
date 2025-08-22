# core/permissions.py
from rest_framework import permissions
# core/permissions.py
from rest_framework import permissions
from django.db.models import Q # Import Q objects for complex lookups
from rest_framework import generics
from .models import Role
from .serializers import RoleSerializer
from rest_framework import serializers
from django.contrib.auth.models import Permission
from rest_framework import serializers, generics

class HasPermission(permissions.BasePermission):
    """
    Custom permission to check if a user has a specific permission
    across all their company memberships.
    """
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        # Superuser check should be at the top for efficiency
        if user.is_superuser:
            return True

        # Use a more robust query to check for the permission
        # This checks if ANY of the user's roles, across ANY of their company memberships,
        # have the required permission.
        return user.usercompanymembership_set.filter(
            roles__permissions__codename=self.permission_codename
        ).exists()
    
# core/views.py
# ... (existing imports)
from .permissions import HasPermission

# Example: A view for managing roles
class RoleManagementView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer # You will need to create this
    permission_classes = [HasPermission('role.create')]

    # We'll need to modify the serializer or view to handle the company field correctly



    # core/serializers.py
# ... (existing imports)

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'description']
        read_only_fields = ['id']

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permission.objects.all()
    )
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'company', 'permissions']
        read_only_fields = ['id', 'company']
# core/views.py
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import (
    User,
    Company,
    UserCompanyMembership,
    Role,
    Permission,
    AuditLog
)
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CompanySerializer,
    RoleSerializer,
    PermissionSerializer,
    UserCompanyMembershipSerializer
)
from .permissions import HasPermission
from .utils import log_action

class CompanyQuerysetMixin:
    """
    A mixin to filter querysets based on the requesting user's company.
    """
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()

        try:
            user_membership = user.usercompanymembership_set.first()
            if not user_membership:
                return self.queryset.none()
            user_company = user_membership.company
        except UserCompanyMembership.DoesNotExist:
            return self.queryset.none()

        return super().get_queryset().filter(company=user_company)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        user = serializer.instance
        log_action(user, 'create', f"New user account created: {user.username}")
        
        return Response({
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)

class UserListView(CompanyQuerysetMixin, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        try:
            user_membership = user.usercompanymembership_set.first()
            if not user_membership:
                return User.objects.none()
            user_company = user_membership.company
            return User.objects.filter(usercompanymembership__company=user_company)
        except UserCompanyMembership.DoesNotExist:
            return User.objects.none()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        instance = self.get_object()
        super().perform_update(serializer)
        log_action(self.request.user, 'update', f"Updated user profile for {instance.username}")

    def perform_destroy(self, instance):
        log_action(self.request.user, 'delete', f"Deleted user: {instance.username}")
        super().perform_destroy(instance)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUser]

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission('permission.view')]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), HasPermission('role.manage')]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Role.objects.all()
        user_company = user.usercompanymembership_set.first().company
        return Role.objects.filter(company=user_company)

    def perform_create(self, serializer):
        user_company = self.request.user.usercompanymembership_set.first().company
        serializer.save(company=user_company)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'delete', f"Deleted role: {instance.name}")
        super().perform_destroy(instance)

class UserCompanyMembershipViewSet(viewsets.ModelViewSet):
    queryset = UserCompanyMembership.objects.all()
    serializer_class = UserCompanyMembershipSerializer
    permission_classes = [IsAuthenticated, HasPermission('user.manage_memberships')]

    def perform_create(self, serializer):
        user_company = self.request.user.usercompanymembership_set.first().company
        serializer.save(company=user_company)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserCompanyMembership.objects.all()
        
        user_company = user.usercompanymembership_set.first().company
        return UserCompanyMembership.objects.filter(company=user_company)
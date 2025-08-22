
# core/urls.py
from .views import CompanyViewSet
from django.urls import path, include
from rest_framework import viewsets
from .models import Company
from .serializers import CompanySerializer


from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserListView,
    UserDetailView,
    CompanyViewSet,
    RoleViewSet,
    PermissionViewSet,
     UserCompanyMembershipViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'memberships', UserCompanyMembershipViewSet)

urlpatterns = [
    # API for user authentication and management
    path('users/register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # API for company, role, and permission management
    path('', include(router.urls)),
]


# router = DefaultRouter()
# router.register(r'companies', CompanyViewSet)
# router.register(r'roles', RoleViewSet)
# router.register(r'permissions', PermissionViewSet)

# urlpatterns = [
#     # API for user authentication and management
#     path('users/register/', UserRegistrationView.as_view(), name='user-register'),
#     path('users/', UserListView.as_view(), name='user-list'),
#     path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

#     # API for company, role, and permission management
#     path('', include(router.urls)),
# ]
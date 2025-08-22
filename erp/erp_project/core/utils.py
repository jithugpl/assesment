# core/utils.py
from .models import AuditLog, UserCompanyMembership
from rest_framework import generics

def log_action(user, action, description):
    try:
        membership = UserCompanyMembership.objects.filter(user=user).first()
        company = membership.company if membership else None

        AuditLog.objects.create(
            user=user,
            company=company,
            action=action,
            description=description
        )
    except Exception as e:
        # Handle logging failures gracefully
        print(f"Failed to create audit log: {e}")

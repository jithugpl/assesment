from django.db import models

# Create your models here.
# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.codename
    

# core/models.py
# ... (other models and imports)

class Role(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return f"{self.name} ({self.company.name})"
    
# core/models.py
# ... (other models and imports)

class User(AbstractUser):
    # Fields for account lockout policy
    failed_login_attempts = models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    # We remove the ForeignKey to company here, as it will be managed by UserCompanyMembership

    @property
    def is_locked_out(self):
        """Returns True if the user's account is currently locked out."""
        return self.lockout_until and timezone.now() < self.lockout_until
    
# core/models.py
# ... (other models and imports)

class UserCompanyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, blank=True)

    class Meta:
        # Ensures a user can only have one membership per company
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.username} @ {self.company.name}"
    
# core/models.py
# ... (other models and imports)

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"